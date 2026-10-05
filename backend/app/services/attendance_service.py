from datetime import datetime, date, timezone

import json

from sqlalchemy.orm import Session

from app.models.entities import (
    Student,
    Faculty,
    Subject,
    Enrollment,
    AttendanceSession,
    AttendanceRecord,
    AuditLog,
)
from app.schemas.attendance import AttendanceRequest


def get_faculty(db: Session, user_id: int):
    """
    Resolve the Faculty profile belonging to the authenticated User.
    """
    return (
        db.query(Faculty)
        .filter(Faculty.user_id == user_id)
        .first()
    )


def validate_attendance(
    db: Session,
    faculty: Faculty,
    request: AttendanceRequest,
):
    """
    Validate an attendance request without modifying the database.

    Returns:
        preview
        enrolled_students
        errors
        warnings
    """

    errors = []
    warnings = []

    # ---------------------------------------------------------
    # 1. Validate subject
    # ---------------------------------------------------------

    subject = (
        db.query(Subject)
        .filter(Subject.code == request.subject_code)
        .first()
    )

    if subject is None:
        errors.append(
            f"Subject '{request.subject_code}' does not exist."
        )
        return None, [], errors, warnings

    # ---------------------------------------------------------
    # 2. Validate date
    # ---------------------------------------------------------

    if request.date > date.today():
        errors.append(
            "Attendance date cannot be in the future."
        )

    # ---------------------------------------------------------
    # 3. Validate faculty
    # ---------------------------------------------------------

    if faculty.department_id != subject.department_id:
        errors.append(
            "Faculty member does not belong to the department "
            "responsible for this subject."
        )

    # ---------------------------------------------------------
    # 4. Validate section
    # ---------------------------------------------------------

    section = request.section.upper()

    if section not in {"A", "B"}:
        errors.append(
            "Section must be either A or B."
        )

    # ---------------------------------------------------------
    # 5. Check duplicate attendance session
    # ---------------------------------------------------------

    existing_session = (
        db.query(AttendanceSession)
        .filter(
            AttendanceSession.subject_id == subject.id,
            AttendanceSession.session_date == request.date,
            AttendanceSession.period == request.period,
            AttendanceSession.section == section,
        )
        .first()
    )

    if existing_session is not None:
        errors.append(
            "Attendance has already been recorded for this "
            "subject, date, period, and section."
        )

    # ---------------------------------------------------------
    # 6. Find enrolled students
    # ---------------------------------------------------------

    enrolled_students = (
        db.query(Student)
        .join(
            Enrollment,
            Enrollment.student_id == Student.id,
        )
        .filter(
            Enrollment.subject_id == subject.id,
            Student.semester == subject.semester,
            Student.section == section,
        )
        .order_by(Student.register_number)
        .all()
    )

    if not enrolled_students:
        errors.append(
            "No enrolled students were found for this subject "
            f"and section {section}."
        )

    # ---------------------------------------------------------
    # 7. Validate absent student IDs
    # ---------------------------------------------------------

    enrolled_ids = {
        student.register_number
        for student in enrolled_students
    }

    absent_ids = set(request.absent_student_ids)

    unknown_absent_ids = absent_ids - enrolled_ids

    if unknown_absent_ids:
        errors.append(
            "The following students are not enrolled in this "
            f"subject/section: {sorted(unknown_absent_ids)}"
        )

    # ---------------------------------------------------------
    # 8. Build attendance lists
    # ---------------------------------------------------------

    present_students = [
        student
        for student in enrolled_students
        if student.register_number not in absent_ids
    ]

    absent_students = [
        student
        for student in enrolled_students
        if student.register_number in absent_ids
    ]

    present_ids = [
        student.register_number
        for student in present_students
    ]

    absent_ids_ordered = [
        student.register_number
        for student in absent_students
    ]

    # ---------------------------------------------------------
    # 9. Warning checks
    # ---------------------------------------------------------

    if len(absent_ids) == 0:
        warnings.append(
            "No absent students were specified. "
            "All enrolled students will be marked PRESENT."
        )

    # ---------------------------------------------------------
    # 10. Build preview
    # ---------------------------------------------------------

    preview = {
        "subject_code": subject.code,
        "subject_name": subject.name,
        "date": request.date,
        "period": request.period,
        "semester": subject.semester,
        "section": section,
        "total_students": len(enrolled_students),
        "present_count": len(present_students),
        "absent_count": len(absent_students),
        "absent_student_ids": absent_ids_ordered,
        "present_student_ids": present_ids,
        "warnings": warnings,
        "status": (
            "VALIDATION_FAILED"
            if errors
            else "READY_FOR_CONFIRMATION"
        ),
    }

    return (
        preview,
        enrolled_students,
        errors,
        warnings,
    )


def commit_attendance(
    db: Session,
    faculty: Faculty,
    request: AttendanceRequest,
):
    """
    Revalidate and commit attendance.

    Database changes:
        1. AttendanceSession
        2. AttendanceRecord for every enrolled student
        3. AuditLog

    All three are committed in ONE database transaction.
    """

    # ---------------------------------------------------------
    # 1. Revalidate before committing
    # ---------------------------------------------------------

    preview, enrolled_students, errors, warnings = validate_attendance(
        db,
        faculty,
        request,
    )

    if errors:
        return {
            "message": "Attendance validation failed",
            "errors": errors,
            "warnings": warnings,
            "preview": preview,
            "status": "VALIDATION_FAILED",
        }

    # ---------------------------------------------------------
    # 2. Resolve subject
    # ---------------------------------------------------------

    subject = (
        db.query(Subject)
        .filter(Subject.code == request.subject_code)
        .first()
    )

    if subject is None:
        return {
            "message": "Subject not found",
            "status": "VALIDATION_FAILED",
        }

    try:
        # -----------------------------------------------------
        # 3. Create AttendanceSession
        # -----------------------------------------------------

        session = AttendanceSession(
            subject_id=subject.id,
            faculty_id=faculty.id,
            session_date=request.date,
            period=request.period,
            semester=subject.semester,
            section=request.section.upper(),
            created_at=datetime.now(timezone.utc),
        )

        db.add(session)

        # Generate session.id before creating records.
        db.flush()

        # -----------------------------------------------------
        # 4. Create AttendanceRecord for every student
        # -----------------------------------------------------

        absent_ids = set(request.absent_student_ids)

        for student in enrolled_students:

            status = (
                "ABSENT"
                if student.register_number in absent_ids
                else "PRESENT"
            )

            record = AttendanceRecord(
                session_id=session.id,
                student_id=student.id,
                status=status,
                marked_at=datetime.now(timezone.utc),
            )

            db.add(record)

        # -----------------------------------------------------
        # 5. Create AuditLog
        # -----------------------------------------------------

        audit_log = AuditLog(
            user_id=faculty.user_id,
            action="ATTENDANCE_COMMITTED",
            entity_type="AttendanceSession",
            entity_id=session.id,
            details=json.dumps({
                "subject_code": subject.code,
                "subject_name": subject.name,
                "date": str(request.date),
                "period": request.period,
                "semester": subject.semester,
                "section": request.section.upper(),
                "total_students": len(enrolled_students),
                "present_count": preview["present_count"],
                "absent_count": preview["absent_count"],
                "absent_student_ids": request.absent_student_ids,
            }),
            created_at=datetime.now(timezone.utc),
        )

        db.add(audit_log)

        # -----------------------------------------------------
        # 6. ONE transaction commit
        # -----------------------------------------------------

        db.commit()

        # Refresh the session so the response contains
        # the persisted database state.
        db.refresh(session)

        return {
            "message": "Attendance committed successfully",
            "session_id": session.id,
            "subject_code": subject.code,
            "subject_name": subject.name,
            "date": request.date,
            "period": request.period,
            "semester": subject.semester,
            "section": request.section.upper(),
            "total_students": len(enrolled_students),
            "present_count": preview["present_count"],
            "absent_count": preview["absent_count"],
            "absent_student_ids": request.absent_student_ids,
            "status": "COMMITTED",
        }

    except Exception as exc:
        # -----------------------------------------------------
        # 7. Roll back the COMPLETE transaction
        # -----------------------------------------------------

        db.rollback()

        raise RuntimeError(
            f"Attendance commit failed: {exc}"
        ) from exc
