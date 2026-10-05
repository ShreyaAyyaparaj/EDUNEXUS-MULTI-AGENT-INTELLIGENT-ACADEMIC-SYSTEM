from sqlalchemy.orm import Session

from app.models.entities import (
    AttendanceRecord,
    AttendanceSession,
    Assessment,
    Enrollment,
    Mark,
    SemesterResult,
    Student,
    Subject,
)


def get_student(db: Session, user_id: int):
    student = (
        db.query(Student)
        .filter(Student.user_id == user_id)
        .first()
    )

    if not student:
        raise ValueError(
            "Student profile not found."
        )

    return student


def get_attendance_summary(
    db: Session,
    student_id: int,
):
    rows = (
        db.query(
            Subject.code,
            Subject.name,
            AttendanceRecord.status,
        )
        .join(
            AttendanceSession,
            AttendanceRecord.session_id
            == AttendanceSession.id,
        )
        .join(
            Subject,
            AttendanceSession.subject_id
            == Subject.id,
        )
        .filter(
            AttendanceRecord.student_id
            == student_id
        )
        .all()
    )

    subject_data = {}

    for code, name, status in rows:
        if code not in subject_data:
            subject_data[code] = {
                "subject_code": code,
                "subject_name": name,
                "present": 0,
                "total": 0,
            }

        subject_data[code]["total"] += 1

        if str(status).upper() == "PRESENT":
            subject_data[code]["present"] += 1

    results = []

    total_present = 0
    total_classes = 0

    for item in subject_data.values():
        percentage = (
            item["present"] / item["total"] * 100
            if item["total"]
            else 0
        )

        total_present += item["present"]
        total_classes += item["total"]

        results.append({
            **item,
            "attendance_percentage": round(
                percentage,
                2,
            ),
        })

    overall_percentage = (
        total_present / total_classes * 100
        if total_classes
        else 0
    )

    return {
        "overall_percentage": round(
            overall_percentage,
            2,
        ),
        "total_present": total_present,
        "total_classes": total_classes,
        "subjects": sorted(
            results,
            key=lambda x: x["attendance_percentage"],
        ),
    }


def get_marks_summary(
    db: Session,
    student_id: int,
):
    rows = (
        db.query(
            Subject.code,
            Subject.name,
            Assessment.name,
            Assessment.max_marks,
            Mark.marks_obtained,
        )
        .join(
            Enrollment,
            Enrollment.subject_id
            == Subject.id,
        )
        .join(
            Assessment,
            Assessment.subject_id
            == Subject.id,
        )
        .join(
            Mark,
            Mark.assessment_id
            == Assessment.id,
        )
        .filter(
            Enrollment.student_id
            == student_id,
            Mark.student_id
            == student_id,
        )
        .all()
    )

    results = []

    for (
        subject_code,
        subject_name,
        assessment_name,
        max_marks,
        marks,
    ) in rows:
        percentage = (
            float(marks)
            / float(max_marks)
            * 100
            if max_marks
            else 0
        )

        results.append({
            "subject_code": subject_code,
            "subject_name": subject_name,
            "assessment": assessment_name,
            "marks": float(marks),
            "max_marks": float(max_marks),
            "percentage": round(
                percentage,
                2,
            ),
        })

    return results


def get_results_summary(
    db: Session,
    student_id: int,
):
    rows = (
        db.query(SemesterResult)
        .filter(
            SemesterResult.student_id
            == student_id
        )
        .order_by(
            SemesterResult.semester
        )
        .all()
    )

    return [
        {
            "semester": result.semester,
            "sgpa": (
                float(result.sgpa)
                if result.sgpa is not None
                else None
            ),
            "cgpa": (
                float(result.cgpa)
                if result.cgpa is not None
                else None
            ),
        }
        for result in rows
    ]


def get_student_success_context(
    db: Session,
    user_id: int,
):
    student = get_student(
        db=db,
        user_id=user_id,
    )

    attendance = get_attendance_summary(
        db=db,
        student_id=student.id,
    )

    marks = get_marks_summary(
        db=db,
        student_id=student.id,
    )

    results = get_results_summary(
        db=db,
        student_id=student.id,
    )

    return {
        "student": {
            "id": student.id,
            "register_number": student.register_number,
            "name": student.name,
            "semester": student.semester,
            "section": student.section,
        },
        "attendance": attendance,
        "marks": marks,
        "results": results,
    }

