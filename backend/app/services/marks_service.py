from datetime import datetime, timezone
import json
from sqlalchemy.orm import Session

from app.models.entities import (
    Student,
    Faculty,
    Subject,
    Enrollment,
    Assessment,
    Mark,
    AuditLog,
)


def get_faculty(db: Session, user_id: int):
    return (
        db.query(Faculty)
        .filter(Faculty.user_id == user_id)
        .first()
    )


def _get_subject_and_assessment(
    db: Session,
    faculty: Faculty,
    subject_code: str,
    assessment_name: str,
):
    """
    Resolve subject and assessment using the database as
    the source of truth.
    """

    errors = []

    subject = (
        db.query(Subject)
        .filter(Subject.code == subject_code.strip().upper())
        .first()
    )

    if subject is None:
        errors.append(
            f"Subject '{subject_code}' does not exist."
        )
        return None, None, errors

    if faculty.department_id != subject.department_id:
        errors.append(
            "Faculty member does not belong to the department "
            "responsible for this subject."
        )

    normalized_assessment_name = " ".join(
        assessment_name.strip().split()
    )

    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.subject_id == subject.id,
            Assessment.name.ilike(normalized_assessment_name),
        )
        .first()
    )

    if assessment is None:
        errors.append(
            f"Assessment '{assessment_name}' does not exist "
            f"for subject '{subject.code}'."
        )
        return subject, None, errors

    return subject, assessment, errors


def _get_enrolled_students(
    db: Session,
    subject: Subject,
):
    return (
        db.query(Student)
        .join(
            Enrollment,
            Enrollment.student_id == Student.id,
        )
        .filter(
            Enrollment.subject_id == subject.id,
            Student.semester == subject.semester,
        )
        .all()
    )


# ============================================================
# ADD NEW MARKS
# ============================================================

def validate_marks(
    db: Session,
    faculty: Faculty,
    subject_code: str,
    assessment_name: str,
    marks: dict[str, float],
):
    errors = []
    warnings = []

    # ---------------------------------------------------------
    # 1. Subject + assessment
    # ---------------------------------------------------------

    subject, assessment, lookup_errors = _get_subject_and_assessment(
        db,
        faculty,
        subject_code,
        assessment_name,
    )

    errors.extend(lookup_errors)

    if subject is None or assessment is None:
        return None, errors, warnings

    # ---------------------------------------------------------
    # 2. Students enrolled in subject
    # ---------------------------------------------------------

    enrolled_students = _get_enrolled_students(
        db,
        subject,
    )

    student_map = {
        student.register_number: student
        for student in enrolled_students
    }

    # ---------------------------------------------------------
    # 3. Validate every mark
    # ---------------------------------------------------------

    preview_records = []

    for register_number, mark_value in marks.items():

        register_number = register_number.strip()

        student = student_map.get(register_number)

        if student is None:
            preview_records.append({
                "register_number": register_number,
                "marks": mark_value,
                "status": "INVALID",
                "reason": "Student is not enrolled in this subject.",
            })
            continue

        try:
            numeric_mark = float(mark_value)
        except (TypeError, ValueError):
            preview_records.append({
                "register_number": register_number,
                "marks": mark_value,
                "status": "INVALID",
                "reason": "Marks must be numeric.",
            })
            continue

        if numeric_mark < 0:
            preview_records.append({
                "register_number": register_number,
                "marks": numeric_mark,
                "status": "INVALID",
                "reason": "Marks cannot be negative.",
            })
            continue

        if numeric_mark > float(assessment.max_marks):
            preview_records.append({
                "register_number": register_number,
                "marks": numeric_mark,
                "status": "INVALID",
                "reason": (
                    f"Marks cannot exceed maximum marks "
                    f"{assessment.max_marks}."
                ),
            })
            continue

        existing_mark = (
            db.query(Mark)
            .filter(
                Mark.student_id == student.id,
                Mark.assessment_id == assessment.id,
            )
            .first()
        )

        if existing_mark is not None:
            preview_records.append({
                "register_number": register_number,
                "marks": numeric_mark,
                "status": "DUPLICATE",
                "reason": "Marks already exist for this assessment.",
            })
            continue

        preview_records.append({
            "register_number": register_number,
            "student_id": student.id,
            "marks": numeric_mark,
            "status": "VALID",
            "reason": None,
        })

    # ---------------------------------------------------------
    # 4. Summary
    # ---------------------------------------------------------

    valid_count = sum(
        1
        for record in preview_records
        if record["status"] == "VALID"
    )

    invalid_count = len(preview_records) - valid_count

    if valid_count == 0:
        errors.append(
            "No valid marks records are available for import."
        )

    preview = {
        "subject_code": subject.code,
        "subject_name": subject.name,
        "assessment_name": assessment.name,
        "assessment_type": assessment.assessment_type,
        "max_marks": float(assessment.max_marks),
        "total_records": len(preview_records),
        "valid_records": valid_count,
        "invalid_records": invalid_count,
        "records": preview_records,
        "errors": errors,
        "warnings": warnings,
        "status": (
            "VALIDATION_FAILED"
            if errors
            else "READY_FOR_CONFIRMATION"
        ),
    }

    return preview, errors, warnings


def commit_marks(
    db: Session,
    faculty: Faculty,
    subject_code: str,
    assessment_name: str,
    marks: dict[str, float],
):
    """
    Revalidate and commit NEW marks + audit log
    in a single transaction.
    """

    preview, errors, warnings = validate_marks(
        db,
        faculty,
        subject_code,
        assessment_name,
        marks,
    )

    if errors:
        return {
            "message": "Marks validation failed",
            "errors": errors,
            "warnings": warnings,
            "preview": preview,
            "status": "VALIDATION_FAILED",
        }

    subject, assessment, lookup_errors = _get_subject_and_assessment(
        db,
        faculty,
        subject_code,
        assessment_name,
    )

    if lookup_errors:
        return {
            "message": "Marks validation failed",
            "errors": lookup_errors,
            "warnings": [],
            "preview": preview,
            "status": "VALIDATION_FAILED",
        }

    try:

        committed = 0

        for record in preview["records"]:

            if record["status"] != "VALID":
                continue

            mark = Mark(
                student_id=record["student_id"],
                assessment_id=assessment.id,
                marks_obtained=record["marks"],
            )

            db.add(mark)
            committed += 1

        audit_log = AuditLog(
    user_id=faculty.user_id,
    action="MARKS_COMMITTED",
    entity_type="ASSESSMENT",
    entity_id=str(assessment.id),
    details=json.dumps({
        "subject_code": subject.code,
        "subject_name": subject.name,
        "assessment_name": assessment.name,
        "assessment_type": assessment.assessment_type,
        "max_marks": float(assessment.max_marks),
        "total_records": preview["total_records"],
        "committed_records": committed,
        "invalid_records": preview["invalid_records"],
    }),
    created_at=datetime.now(timezone.utc),
)

        db.add(audit_log)

        db.commit()

        return {
            "message": "Marks committed successfully",
            "assessment_id": assessment.id,
            "subject_code": subject.code,
            "subject_name": subject.name,
            "assessment_name": assessment.name,
            "committed_records": committed,
            "invalid_records": preview["invalid_records"],
            "status": "COMMITTED",
        }

    except Exception as exc:

        db.rollback()

        raise RuntimeError(
            f"Marks commit failed: {exc}"
        ) from exc


# ============================================================
# UPDATE EXISTING MARKS
# ============================================================

def validate_mark_updates(
    db: Session,
    faculty: Faculty,
    subject_code: str,
    assessment_name: str,
    marks: dict[str, float],
):
    """
    Validate explicit updates to existing academic marks.

    Existing marks are REQUIRED here.
    Missing marks are rejected because this function is only
    for updates.
    """

    errors = []
    warnings = []

    # ---------------------------------------------------------
    # 1. Subject + assessment
    # ---------------------------------------------------------

    subject, assessment, lookup_errors = _get_subject_and_assessment(
        db,
        faculty,
        subject_code,
        assessment_name,
    )

    errors.extend(lookup_errors)

    if subject is None or assessment is None:
        return None, errors, warnings

    # ---------------------------------------------------------
    # 2. Students enrolled in subject
    # ---------------------------------------------------------

    enrolled_students = _get_enrolled_students(
        db,
        subject,
    )

    student_map = {
        student.register_number: student
        for student in enrolled_students
    }

    # ---------------------------------------------------------
    # 3. Validate updates
    # ---------------------------------------------------------

    preview_records = []

    for register_number, mark_value in marks.items():

        register_number = register_number.strip()

        student = student_map.get(register_number)

        if student is None:
            preview_records.append({
                "register_number": register_number,
                "marks": mark_value,
                "status": "INVALID",
                "reason": "Student is not enrolled in this subject.",
            })
            continue

        try:
            numeric_mark = float(mark_value)
        except (TypeError, ValueError):
            preview_records.append({
                "register_number": register_number,
                "marks": mark_value,
                "status": "INVALID",
                "reason": "Marks must be numeric.",
            })
            continue

        if numeric_mark < 0:
            preview_records.append({
                "register_number": register_number,
                "marks": numeric_mark,
                "status": "INVALID",
                "reason": "Marks cannot be negative.",
            })
            continue

        if numeric_mark > float(assessment.max_marks):
            preview_records.append({
                "register_number": register_number,
                "marks": numeric_mark,
                "status": "INVALID",
                "reason": (
                    f"Marks cannot exceed maximum marks "
                    f"{assessment.max_marks}."
                ),
            })
            continue

        existing_mark = (
            db.query(Mark)
            .filter(
                Mark.student_id == student.id,
                Mark.assessment_id == assessment.id,
            )
            .first()
        )

        if existing_mark is None:
            preview_records.append({
                "register_number": register_number,
                "marks": numeric_mark,
                "status": "NOT_FOUND",
                "reason": (
                    "No existing mark was found. "
                    "Use Add Marks for new records."
                ),
            })
            continue

        current_mark = float(existing_mark.marks_obtained)

        if current_mark == numeric_mark:
            preview_records.append({
                "register_number": register_number,
                "student_id": student.id,
                "mark_id": existing_mark.id,
                "current_marks": current_mark,
                "new_marks": numeric_mark,
                "marks": numeric_mark,
                "status": "NO_CHANGE",
                "reason": "New mark is identical to the existing mark.",
            })
            continue

        preview_records.append({
            "register_number": register_number,
            "student_id": student.id,
            "mark_id": existing_mark.id,
            "current_marks": current_mark,
            "new_marks": numeric_mark,
            "marks": numeric_mark,
            "status": "UPDATE",
            "reason": None,
        })

    # ---------------------------------------------------------
    # 4. Summary
    # ---------------------------------------------------------

    update_count = sum(
        1
        for record in preview_records
        if record["status"] == "UPDATE"
    )

    invalid_count = sum(
        1
        for record in preview_records
        if record["status"] in {"INVALID", "NOT_FOUND"}
    )

    no_change_count = sum(
        1
        for record in preview_records
        if record["status"] == "NO_CHANGE"
    )

    if update_count == 0:
        errors.append(
            "No marks are available for update."
        )

    preview = {
        "subject_code": subject.code,
        "subject_name": subject.name,
        "assessment_name": assessment.name,
        "assessment_type": assessment.assessment_type,
        "max_marks": float(assessment.max_marks),
        "total_records": len(preview_records),
        "update_records": update_count,
        "invalid_records": invalid_count,
        "no_change_records": no_change_count,
        "records": preview_records,
        "errors": errors,
        "warnings": warnings,
        "status": (
            "VALIDATION_FAILED"
            if errors
            else "READY_FOR_CONFIRMATION"
        ),
    }

    return preview, errors, warnings


def commit_mark_updates(
    db: Session,
    faculty: Faculty,
    subject_code: str,
    assessment_name: str,
    marks: dict[str, float],
):
    """
    Revalidate and explicitly UPDATE existing marks.

    Every update records:
        - student
        - old mark
        - new mark
        - assessment
        - faculty user

    The entire operation is committed as one transaction.
    """

    preview, errors, warnings = validate_mark_updates(
        db,
        faculty,
        subject_code,
        assessment_name,
        marks,
    )

    if errors:
        return {
            "message": "Mark update validation failed",
            "errors": errors,
            "warnings": warnings,
            "preview": preview,
            "status": "VALIDATION_FAILED",
        }

    subject, assessment, lookup_errors = _get_subject_and_assessment(
        db,
        faculty,
        subject_code,
        assessment_name,
    )

    if lookup_errors:
        return {
            "message": "Mark update validation failed",
            "errors": lookup_errors,
            "warnings": [],
            "preview": preview,
            "status": "VALIDATION_FAILED",
        }

    try:

        updated_records = []

        for record in preview["records"]:

            if record["status"] != "UPDATE":
                continue

            mark = (
                db.query(Mark)
                .filter(
                    Mark.id == record["mark_id"],
                    Mark.student_id == record["student_id"],
                    Mark.assessment_id == assessment.id,
                )
                .first()
            )

            if mark is None:
                raise RuntimeError(
                    "A mark changed between validation and confirmation. "
                    "Please validate again."
                )

            old_marks = float(mark.marks_obtained)
            new_marks = float(record["new_marks"])

            mark.marks_obtained = new_marks

            updated_records.append({
                "register_number": record["register_number"],
                "mark_id": mark.id,
                "old_marks": old_marks,
                "new_marks": new_marks,
            })

        audit_log = AuditLog(
    user_id=faculty.user_id,
    action="MARKS_UPDATED",
    entity_type="Assessment",
    entity_id=assessment.id,
    details=json.dumps({
        "subject_code": subject.code,
        "subject_name": subject.name,
        "assessment_name": assessment.name,
        "assessment_type": assessment.assessment_type,
        "max_marks": float(assessment.max_marks),
        "total_records": preview["total_records"],
        "updated_count": len(updated_records),
        "invalid_records": preview["invalid_records"],
        "no_change_records": preview["no_change_records"],
        "updates": updated_records,
    }),
    created_at=datetime.now(timezone.utc),
)

        db.add(audit_log)

        db.commit()

        return {
            "message": "Marks updated successfully",
            "assessment_id": assessment.id,
            "subject_code": subject.code,
            "subject_name": subject.name,
            "assessment_name": assessment.name,
            "updated_records": len(updated_records),
            "invalid_records": preview["invalid_records"],
            "no_change_records": preview["no_change_records"],
            "updates": updated_records,
            "status": "UPDATED",
        }

    except Exception as exc:

        db.rollback()

        raise RuntimeError(
            f"Mark update failed: {exc}"
        ) from exc
