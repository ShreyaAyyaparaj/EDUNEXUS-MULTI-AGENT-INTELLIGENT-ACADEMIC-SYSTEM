from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_student
from app.db.database import get_db
from app.models.entities import (
    User,
    Student,
    Enrollment,
    AttendanceRecord,
    AttendanceSession,
    Mark,
    Assessment,
    SemesterResult,
    Resource,
    Achievement,
    Subject,
)

router = APIRouter(
    prefix="/api/student",
    tags=["Student"],
)


RESOURCE_STORAGE = Path(__file__).resolve().parents[2] / "storage" / "evaluation1"

def _resource_file_available(resource: Resource) -> bool:
    if not resource.file_path:
        return False
    path = Path(resource.file_path)
    try:
        path.resolve().relative_to(RESOURCE_STORAGE.resolve())
    except ValueError:
        return False
    return path.is_file()


def get_student(
    current_user: User,
    db: Session,
) -> Student:
    student = (
        db.query(Student)
        .filter(Student.user_id == current_user.id)
        .first()
    )

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found",
        )

    return student


@router.get("/dashboard")
def student_dashboard(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    student = get_student(current_user, db)

    results = (
        db.query(SemesterResult)
        .filter(SemesterResult.student_id == student.id)
        .order_by(SemesterResult.semester.desc())
        .all()
    )

    attendance_records = (
        db.query(AttendanceRecord)
        .filter(AttendanceRecord.student_id == student.id)
        .all()
    )

    marks = (
        db.query(Mark)
        .filter(Mark.student_id == student.id)
        .all()
    )

    achievements = (
        db.query(Achievement)
        .filter(Achievement.student_id == student.id)
        .all()
    )

    # Current-semester subjects for this specific student.
    # We use both Enrollment and Subject.semester so that
    # the dashboard does not show unrelated subjects or
    # historical assessment records as "subjects".
    current_subjects = (
        db.query(Subject)
        .join(
            Enrollment,
            Enrollment.subject_id == Subject.id,
        )
        .filter(
            Enrollment.student_id == student.id,
            Subject.semester == student.semester,
        )
        .order_by(Subject.code.asc())
        .all()
    )

    latest_result = results[0] if results else None

    total_attendance = len(attendance_records)

    present_attendance = sum(
        1
        for record in attendance_records
        if str(record.status).upper() == "PRESENT"
    )

    attendance_percentage = (
        round((present_attendance / total_attendance) * 100, 2)
        if total_attendance
        else 0
    )

    return {
        "student": {
            "id": student.id,
            "register_number": student.register_number,
            "name": student.name,
            "semester": student.semester,
            "section": student.section,
            "batch": student.batch,
            "department_name": student.department.name,
        },
        "academic": {
            "current_semester": student.semester,
            "cgpa": student.cgpa,
            "latest_sgpa": (
                latest_result.sgpa
                if latest_result
                else None
            ),
        },
        "current_semester_subjects": [
            {
                "id": subject.id,
                "code": subject.code,
                "name": subject.name,
                "credits": subject.credits,
            }
            for subject in current_subjects
        ],
        "attendance": {
            "total_records": total_attendance,
            "present_records": present_attendance,
            "percentage": attendance_percentage,
        },
        "statistics": {
            "subject_count": len(current_subjects),
            "assessment_records": len(marks),
            "achievements": len(achievements),
        },
    }

@router.get("/attendance")
def student_attendance(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    student = get_student(current_user, db)

    rows = (
        db.query(
            Subject.id,
            Subject.code,
            Subject.name,
            AttendanceRecord.status,
        )
        .join(
            AttendanceSession,
            AttendanceRecord.session_id == AttendanceSession.id,
        )
        .join(
            Subject,
            AttendanceSession.subject_id == Subject.id,
        )
        .filter(
            AttendanceRecord.student_id == student.id
        )
        .all()
    )

    grouped = {}
    for subject_id, code, name, status in rows:
        item = grouped.setdefault(subject_id, {"subject_id": subject_id, "subject_code": code,
            "subject_name": name, "present": 0, "total": 0})
        item["total"] += 1
        if str(status).upper() == "PRESENT":
            item["present"] += 1
    current_subjects = (db.query(Subject).join(Enrollment, Enrollment.subject_id == Subject.id)
        .filter(Enrollment.student_id == student.id, Subject.semester == student.semester).all())
    for subject in current_subjects:
        grouped.setdefault(subject.id, {"subject_id": subject.id, "subject_code": subject.code,
            "subject_name": subject.name, "present": 0, "total": 0})
    data = [{**item, "attendance_percentage": round(item["present"] * 100 / item["total"], 2)
             if item["total"] else None}
            for item in sorted(grouped.values(), key=lambda value: value["subject_code"])]

    return {
        "student_id": student.id,
        "attendance": data,
    }


@router.get("/marks")
def student_marks(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    student = get_student(current_user, db)

    rows = (
        db.query(
            Mark,
            Assessment,
            Subject,
        )
        .join(
            Assessment,
            Mark.assessment_id == Assessment.id,
        )
        .join(
            Subject,
            Assessment.subject_id == Subject.id,
        )
        .filter(
            Mark.student_id == student.id
        )
        .order_by(
            Assessment.assessment_date.desc()
        )
        .all()
    )

    data = []

    for mark, assessment, subject in rows:
        data.append({
            "subject_id": subject.id,
            "subject_code": subject.code,
            "subject_name": subject.name,
            "assessment": assessment.name,
            "assessment_type": assessment.assessment_type,
            "max_marks": assessment.max_marks,
            "marks_obtained": mark.marks_obtained,
            "assessment_date": assessment.assessment_date,
        })

    return {
        "student_id": student.id,
        "marks": data,
    }


@router.get("/results")
def student_results(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    student = get_student(current_user, db)

    results = (
        db.query(SemesterResult)
        .filter(SemesterResult.student_id == student.id)
        .order_by(SemesterResult.semester.asc())
        .all()
    )

    return {
        "student_id": student.id,
        "results": [
            {
                "semester": result.semester,
                "sgpa": result.sgpa,
                "cgpa": result.cgpa,
                "total_credits": result.total_credits,
                "academic_year": result.academic_year,
            }
            for result in results
        ],
    }


@router.get("/resources")
def student_resources(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    student = get_student(current_user, db)

    enrolled_subject_ids = [
        row[0]
        for row in (
            db.query(Enrollment.subject_id)
            .filter(Enrollment.student_id == student.id)
            .all()
        )
    ]

    if not enrolled_subject_ids:
        return {
            "student_id": student.id,
            "resources": [],
        }

    rows = (
        db.query(
            Resource,
            Subject,
        )
        .join(
            Subject,
            Resource.subject_id == Subject.id,
        )
        .filter(
            Resource.subject_id.in_(enrolled_subject_ids)
        )
        .order_by(
            Resource.uploaded_at.desc()
        )
        .all()
    )

    data = []

    for resource, subject in rows:
        data.append({
            "id": resource.id,
            "subject_id": resource.subject_id,
            "subject_code": subject.code,
            "subject_name": subject.name,
            "title": resource.title,
            "description": resource.description,
            "file_name": resource.file_name,
            "file_url": f"/api/resources/{resource.id}/file" if _resource_file_available(resource) else None,
            "resource_type": resource.resource_type,
            "uploaded_at": resource.uploaded_at,
        })

    return {
        "student_id": student.id,
        "resources": data,
    }


@router.get("/achievements")
def student_achievements(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    student = get_student(current_user, db)

    achievements = (
        db.query(Achievement)
        .filter(Achievement.student_id == student.id)
        .order_by(Achievement.created_at.desc())
        .all()
    )

    return {
        "student_id": student.id,
        "achievements": [
            {
                "id": achievement.id,
                "title": achievement.title,
                "category": achievement.category,
                "description": achievement.description,
                "achievement_date": achievement.achievement_date,
                "certificate_name": achievement.certificate_name,
                "certificate_url": f"/api/achievements/{achievement.id}/certificate" if achievement.certificate_path else None,
                "verification_status": achievement.verification_status,
                "faculty_message": achievement.faculty_message,
                "created_at": achievement.created_at,
            }
            for achievement in achievements
        ],
    }

