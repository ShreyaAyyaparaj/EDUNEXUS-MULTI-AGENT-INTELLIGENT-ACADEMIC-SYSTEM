from datetime import date, datetime
import json
from pathlib import Path
import smtplib
from email.message import EmailMessage
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin, require_faculty, require_student
from app.core.security import hash_password
from app.db.database import get_db, settings
from app.models.entities import (
    Achievement, AttendanceRecord, AttendanceSession, AuditLog, Department,
    Enrollment, Faculty, Mark, Assessment, MentorRequest, Notification,
    Resource, Student, Subject, User,
)
from app.schemas.attendance import AttendanceRequest
from app.services.attendance_service import commit_attendance
from app.services.marks_service import commit_marks

router = APIRouter(tags=["Academic workflows"])
UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "storage" / "evaluation1"
MAX_UPLOAD = 10 * 1024 * 1024
ALLOWED_UPLOADS = {".pdf", ".png", ".jpg", ".jpeg", ".doc", ".docx", ".ppt", ".pptx", ".csv", ".xlsx", ".txt"}


def _audit(db, user_id, action, entity, entity_id, details):
    db.add(AuditLog(user_id=user_id, action=action, entity_type=entity,
                    entity_id=str(entity_id), details=json.dumps(details, default=str)))


def _notify(db, user_id, title, message):
    db.add(Notification(user_id=user_id, title=title, message=message, is_read=False))


def _student(db, user):
    item = db.query(Student).filter_by(user_id=user.id).first()
    if not item:
        raise HTTPException(404, "Student profile not found")
    return item


def _faculty(db, user):
    item = db.query(Faculty).filter_by(user_id=user.id).first()
    if not item:
        raise HTTPException(404, "Faculty profile not found")
    return item


def _store_upload(upload: UploadFile | None):
    if not upload or not upload.filename:
        return None, None
    ext = Path(upload.filename).suffix.lower()
    if ext not in ALLOWED_UPLOADS:
        raise HTTPException(400, "Unsupported file type")
    content = upload.file.read(MAX_UPLOAD + 1)
    if len(content) > MAX_UPLOAD:
        raise HTTPException(413, "File exceeds 10 MB")
    if not content:
        raise HTTPException(400, "Uploaded file is empty")
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    name = f"{uuid4().hex}{ext}"
    path = UPLOAD_ROOT / name
    path.write_bytes(content)
    return upload.filename[:255], str(path)


def _stored_file_available(value: str | None) -> bool:
    if not value:
        return False
    path = Path(value)
    try:
        path.resolve().relative_to(UPLOAD_ROOT.resolve())
    except ValueError:
        return False
    return path.is_file()


def _email_faculty(faculty, student, request):
    host = settings.SMTP_HOST
    recipient = faculty.user.email if faculty.user else None
    if not host or not recipient:
        return "NOT_CONFIGURED"
    message = EmailMessage()
    message["Subject"] = f"EduNexus mentor request: {request.project_domain}"
    message["From"] = settings.SMTP_FROM
    message["To"] = recipient
    message.set_content(
        f"Student: {student.name}\nRegister: {student.register_number}\n"
        f"Department: {student.department.name}\nSemester: {student.semester}\n"
        f"Current CGPA: {student.cgpa if student.cgpa is not None else 'Not available'}\n"
        f"Project domain: {request.project_domain}\nQuery: {request.query}\n"
        f"Description: {request.description}"
    )
    try:
        with smtplib.SMTP(host, settings.SMTP_PORT, timeout=5) as smtp:
            if settings.SMTP_USER:
                smtp.starttls()
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.send_message(message)
        return "SENT"
    except Exception:
        return "FAILED"


class Decision(BaseModel):
    status: str
    message: str = Field(default="", max_length=4000)


class ManualAttendance(BaseModel):
    subject_code: str
    date: date
    period: int = Field(ge=1, le=10)
    section: str
    absent_student_ids: list[str]


class ManualMarks(BaseModel):
    subject_code: str
    assessment_name: str
    marks: dict[str, float]


@router.post("/api/student/achievements", status_code=201)
def submit_achievement(title: str = Form(...), category: str = Form(...),
                       description: str = Form(""), achievement_date: date | None = Form(None),
                       certificate: UploadFile | None = File(None),
                       user: User = Depends(require_student), db: Session = Depends(get_db)):
    student = _student(db, user)
    if not title.strip() or not category.strip():
        raise HTTPException(422, "Title and category are required")
    file_name, file_path = _store_upload(certificate)
    item = Achievement(student_id=student.id, title=title.strip(), category=category.strip(),
                       description=description.strip(), achievement_date=achievement_date,
                       certificate_name=file_name, certificate_path=file_path,
                       verification_status="PENDING")
    try:
        db.add(item)
        db.flush()
        _audit(db, user.id, "ACHIEVEMENT_SUBMITTED", "Achievement", item.id, {"title": item.title})
        faculty_ids = db.query(Faculty.user_id).filter(Faculty.department_id == student.department_id).all()
        for (faculty_user_id,) in faculty_ids:
            _notify(db, faculty_user_id, "Achievement submitted", f"{student.name} submitted {item.title} for review.")
        db.commit()
    except Exception:
        db.rollback()
        if file_path:
            Path(file_path).unlink(missing_ok=True)
        raise
    return {"id": item.id, "status": item.verification_status}


@router.post("/api/student/mentor-requests", status_code=201)
def create_mentor_request(faculty_id: int = Form(...), project_domain: str = Form(...),
                          query: str = Form(...), description: str = Form(...),
                          user: User = Depends(require_student), db: Session = Depends(get_db)):
    student = _student(db, user)
    faculty = db.query(Faculty).filter_by(id=faculty_id, department_id=student.department_id).first()
    if not faculty:
        raise HTTPException(404, "Faculty not found in the student's department")
    if not project_domain.strip() or not query.strip() or not description.strip():
        raise HTTPException(422, "Project domain, query, and description are required")
    duplicate = db.query(MentorRequest).filter_by(student_id=student.id, faculty_id=faculty.id, status="PENDING").first()
    if duplicate:
        raise HTTPException(409, "A pending request already exists for this faculty member")
    item = MentorRequest(student_id=student.id, faculty_id=faculty.id, project_domain=project_domain.strip(),
                         query=query.strip(), description=description.strip())
    try:
        db.add(item)
        db.flush()
        if faculty.user_id:
            _notify(db, faculty.user_id, "New mentor request", f"{student.name} requested support in {item.project_domain}.")
        _audit(db, user.id, "MENTOR_REQUEST_SUBMITTED", "MentorRequest", item.id,
               {"faculty_id": faculty.id, "domain": item.project_domain})
        db.commit()
    except Exception:
        db.rollback()
        raise
    item.email_status = _email_faculty(faculty, student, item)
    _audit(db, user.id, f"MENTOR_EMAIL_{item.email_status}", "MentorRequest", item.id,
           {"faculty_id": faculty.id, "email_status": item.email_status})
    db.commit()
    return {"id": item.id, "status": item.status, "email_status": item.email_status}


@router.get("/api/student/mentor-requests")
def student_mentor_requests(user: User = Depends(require_student), db: Session = Depends(get_db)):
    student = _student(db, user)
    rows = db.query(MentorRequest, Faculty).join(Faculty, Faculty.id == MentorRequest.faculty_id).filter(
        MentorRequest.student_id == student.id).order_by(MentorRequest.created_at.desc()).all()
    return {"requests": [{"id": r.id, "faculty_id": f.id, "faculty": f.name,
             "project_domain": r.project_domain, "query": r.query, "description": r.description,
             "status": r.status, "faculty_message": r.faculty_message,
             "email_status": r.email_status, "created_at": r.created_at} for r, f in rows]}


@router.get("/api/faculty/mentor-requests")
def faculty_mentor_requests(user: User = Depends(require_faculty), db: Session = Depends(get_db)):
    faculty = _faculty(db, user)
    rows = db.query(MentorRequest, Student).join(Student, Student.id == MentorRequest.student_id).filter(
        MentorRequest.faculty_id == faculty.id).order_by(MentorRequest.created_at.desc()).all()
    return {"requests": [{"id": r.id, "student": s.name, "register_number": s.register_number,
             "department": s.department.name, "semester": s.semester, "project_domain": r.project_domain,
             "query": r.query, "description": r.description, "status": r.status,
             "faculty_message": r.faculty_message, "created_at": r.created_at} for r, s in rows]}


@router.post("/api/faculty/mentor-requests/{request_id}/decision")
def decide_mentor_request(request_id: int, decision: Decision, user: User = Depends(require_faculty),
                          db: Session = Depends(get_db)):
    faculty = _faculty(db, user)
    status = decision.status.upper()
    if status not in {"APPROVED", "REJECTED", "CLOSED"}:
        raise HTTPException(422, "Status must be APPROVED, REJECTED, or CLOSED")
    item = db.query(MentorRequest).filter_by(id=request_id, faculty_id=faculty.id).with_for_update().first()
    if not item:
        raise HTTPException(404, "Mentor request not found")
    if item.status != "PENDING" and not (item.status == "APPROVED" and status == "CLOSED"):
        raise HTTPException(409, "This request cannot transition to the requested status")
    item.status, item.faculty_message = status, decision.message.strip() or None
    student = db.get(Student, item.student_id)
    _notify(db, student.user_id, f"Mentor request {status.lower()}", decision.message.strip() or f"Your request was {status.lower()}.")
    _audit(db, user.id, f"MENTOR_REQUEST_{status}", "MentorRequest", item.id, {"message": item.faculty_message})
    db.commit()
    return {"id": item.id, "status": item.status, "faculty_message": item.faculty_message}


@router.get("/api/faculty/achievement-reviews")
def achievement_reviews(user: User = Depends(require_faculty), db: Session = Depends(get_db)):
    faculty = _faculty(db, user)
    rows = db.query(Achievement, Student).join(Student, Student.id == Achievement.student_id).filter(
        Student.department_id == faculty.department_id).order_by(Achievement.created_at.desc()).all()
    return {"achievements": [{"id": a.id, "student": s.name, "register_number": s.register_number,
             "title": a.title, "category": a.category, "description": a.description,
             "achievement_date": a.achievement_date, "certificate_name": a.certificate_name,
             "certificate_url": f"/api/achievements/{a.id}/certificate" if a.certificate_path else None,
             "status": a.verification_status, "faculty_message": a.faculty_message} for a, s in rows]}


@router.post("/api/faculty/achievement-reviews/{achievement_id}/decision")
def review_achievement(achievement_id: int, decision: Decision, user: User = Depends(require_faculty),
                       db: Session = Depends(get_db)):
    faculty = _faculty(db, user)
    status = decision.status.upper()
    if status not in {"APPROVED", "REJECTED"}:
        raise HTTPException(422, "Status must be APPROVED or REJECTED")
    item = db.query(Achievement).join(Student, Student.id == Achievement.student_id).filter(
        Achievement.id == achievement_id, Student.department_id == faculty.department_id).with_for_update().first()
    if not item:
        raise HTTPException(404, "Achievement not found")
    if item.verification_status != "PENDING":
        raise HTTPException(409, "Achievement has already been reviewed")
    item.verification_status, item.faculty_message = status, decision.message.strip() or None
    item.reviewed_by, item.reviewed_at = faculty.id, datetime.utcnow()
    student = db.get(Student, item.student_id)
    _notify(db, student.user_id, f"Achievement {status.lower()}", decision.message.strip() or f"Your achievement was {status.lower()}.")
    _audit(db, user.id, f"ACHIEVEMENT_{status}", "Achievement", item.id, {"message": item.faculty_message})
    db.commit()
    return {"id": item.id, "status": item.verification_status, "faculty_message": item.faculty_message}


@router.get("/api/faculty/directory")
def faculty_directory(user: User = Depends(require_student), db: Session = Depends(get_db)):
    student = _student(db, user)
    rows = db.query(Faculty).filter_by(department_id=student.department_id).order_by(Faculty.name).all()
    return {"faculty": [{"id": f.id, "name": f.name, "designation": f.designation} for f in rows]}


@router.get("/api/notifications")
def notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Notification).filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(100).all()
    return {"notifications": [{"id": n.id, "title": n.title, "message": n.message,
             "is_read": n.is_read, "created_at": n.created_at} for n in rows]}


@router.post("/api/notifications/{notification_id}/read")
def mark_notification_read(notification_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(Notification).filter_by(id=notification_id, user_id=user.id).first()
    if not item:
        raise HTTPException(404, "Notification not found")
    item.is_read = True
    db.commit()
    return {"id": item.id, "is_read": True}


@router.get("/api/faculty/subjects")
def faculty_subjects(user: User = Depends(require_faculty), db: Session = Depends(get_db)):
    faculty = _faculty(db, user)
    rows = db.query(Subject).filter_by(department_id=faculty.department_id).order_by(Subject.semester, Subject.code).all()
    return {"subjects": [{"id": s.id, "code": s.code, "name": s.name, "semester": s.semester} for s in rows]}


@router.post("/api/faculty/attendance/manual/confirm")
def manual_attendance(data: ManualAttendance, user: User = Depends(require_faculty), db: Session = Depends(get_db)):
    faculty = _faculty(db, user)
    request = AttendanceRequest(**data.model_dump())
    result = commit_attendance(db, faculty, request)
    return result


@router.post("/api/faculty/marks/manual/confirm")
def manual_marks(data: ManualMarks, user: User = Depends(require_faculty), db: Session = Depends(get_db)):
    faculty = _faculty(db, user)
    return commit_marks(db, faculty, data.subject_code, data.assessment_name, data.marks)


@router.get("/api/faculty/resources")
def faculty_resources(user: User = Depends(require_faculty), db: Session = Depends(get_db)):
    faculty = _faculty(db, user)
    rows = db.query(Resource, Subject).join(Subject, Subject.id == Resource.subject_id).filter(
        Resource.faculty_id == faculty.id).order_by(Resource.uploaded_at.desc()).all()
    return {"resources": [{"id": r.id, "subject_id": s.id, "subject_code": s.code, "subject_name": s.name,
             "title": r.title, "description": r.description, "resource_type": r.resource_type,
             "file_name": r.file_name, "file_url": f"/api/resources/{r.id}/file" if _stored_file_available(r.file_path) else None,
             "uploaded_at": r.uploaded_at} for r, s in rows]}


@router.post("/api/faculty/resources", status_code=201)
def create_resource(title: str = Form(...), description: str = Form(""), subject_id: int = Form(...),
                    resource_type: str = Form("DOCUMENT"), file: UploadFile | None = File(None),
                    user: User = Depends(require_faculty), db: Session = Depends(get_db)):
    faculty = _faculty(db, user)
    subject = db.query(Subject).filter_by(id=subject_id, department_id=faculty.department_id).first()
    if not subject:
        raise HTTPException(404, "Subject not found")
    if not title.strip():
        raise HTTPException(422, "Title is required")
    file_name, path = _store_upload(file)
    item = Resource(subject_id=subject.id, faculty_id=faculty.id, title=title.strip(),
                    description=description.strip(), resource_type=resource_type.strip().upper(),
                    file_name=file_name, file_path=path)
    try:
        db.add(item)
        db.flush()
        _audit(db, user.id, "RESOURCE_CREATED", "Resource", item.id, {"title": item.title})
        db.commit()
    except Exception:
        db.rollback()
        if path:
            Path(path).unlink(missing_ok=True)
        raise
    return {"id": item.id, "title": item.title}


@router.patch("/api/faculty/resources/{resource_id}")
def update_resource(resource_id: int, title: str = Form(...), description: str = Form(""),
                    subject_id: int = Form(...), resource_type: str = Form("DOCUMENT"),
                    user: User = Depends(require_faculty), db: Session = Depends(get_db)):
    faculty = _faculty(db, user)
    item = db.query(Resource).filter_by(id=resource_id, faculty_id=faculty.id).first()
    subject = db.query(Subject).filter_by(id=subject_id, department_id=faculty.department_id).first()
    if not item or not subject:
        raise HTTPException(404, "Resource or subject not found")
    item.title, item.description, item.subject_id = title.strip(), description.strip(), subject.id
    item.resource_type = resource_type.strip().upper()
    _audit(db, user.id, "RESOURCE_UPDATED", "Resource", item.id, {"title": item.title})
    db.commit()
    return {"id": item.id, "title": item.title}


@router.delete("/api/faculty/resources/{resource_id}", status_code=204)
def delete_resource(resource_id: int, user: User = Depends(require_faculty), db: Session = Depends(get_db)):
    faculty = _faculty(db, user)
    item = db.query(Resource).filter_by(id=resource_id, faculty_id=faculty.id).first()
    if not item:
        raise HTTPException(404, "Resource not found")
    path = item.file_path
    _audit(db, user.id, "RESOURCE_DELETED", "Resource", item.id, {"title": item.title})
    db.delete(item)
    db.commit()
    if path:
        try:
            Path(path).resolve().relative_to(UPLOAD_ROOT.resolve())
            Path(path).unlink(missing_ok=True)
        except (ValueError, OSError):
            pass


@router.get("/api/resources/{resource_id}/file")
def download_resource(resource_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(Resource).filter_by(id=resource_id).first()
    if not item or not item.file_path:
        raise HTTPException(404, "Resource file not found")
    allowed = user.role.upper() == "ADMIN"
    faculty = db.query(Faculty).filter_by(user_id=user.id).first()
    if faculty and item.faculty_id == faculty.id:
        allowed = True
    student = db.query(Student).filter_by(user_id=user.id).first()
    if student and db.query(Enrollment).filter_by(student_id=student.id, subject_id=item.subject_id).first():
        allowed = True
    if not allowed:
        raise HTTPException(403, "You are not allowed to download this resource")
    path = Path(item.file_path)
    try:
        path.resolve().relative_to(UPLOAD_ROOT.resolve())
    except ValueError:
        raise HTTPException(404, "Resource file not found")
    if not path.is_file():
        raise HTTPException(404, "Resource file not found")
    return FileResponse(path, filename=item.file_name or path.name)


@router.get("/api/achievements/{achievement_id}/certificate")
def download_achievement_certificate(achievement_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(Achievement).filter_by(id=achievement_id).first()
    if not item or not item.certificate_path:
        raise HTTPException(404, "Certificate not found")
    allowed = user.role.upper() == "ADMIN"
    student = db.query(Student).filter_by(user_id=user.id).first()
    if student and student.id == item.student_id:
        allowed = True
    faculty = db.query(Faculty).filter_by(user_id=user.id).first()
    owner = db.get(Student, item.student_id)
    if faculty and owner and faculty.department_id == owner.department_id:
        allowed = True
    if not allowed:
        raise HTTPException(403, "You are not allowed to download this certificate")
    path = Path(item.certificate_path)
    try:
        path.resolve().relative_to(UPLOAD_ROOT.resolve())
    except ValueError:
        raise HTTPException(404, "Certificate not found")
    if not path.is_file():
        raise HTTPException(404, "Certificate not found")
    return FileResponse(path, filename=item.certificate_name or path.name)


@router.get("/api/faculty/subjects/{subject_id}/roster")
def subject_roster(subject_id: int, section: str, user: User = Depends(require_faculty), db: Session = Depends(get_db)):
    faculty = _faculty(db, user)
    subject = db.query(Subject).filter_by(id=subject_id, department_id=faculty.department_id).first()
    if not subject:
        raise HTTPException(404, "Subject not found")
    rows = db.query(Student).join(Enrollment, Enrollment.student_id == Student.id).filter(
        Enrollment.subject_id == subject.id, Subject.semester == subject.semester,
        Student.semester == subject.semester, Student.section == section).order_by(Student.register_number).all()
    return {"students": [{"id": s.id, "register_number": s.register_number, "name": s.name,
             "department": s.department.name, "section": s.section} for s in rows]}


@router.get("/api/faculty/subjects/{subject_id}/assessments")
def subject_assessments(subject_id: int, user: User = Depends(require_faculty), db: Session = Depends(get_db)):
    faculty = _faculty(db, user)
    subject = db.query(Subject).filter_by(id=subject_id, department_id=faculty.department_id).first()
    if not subject:
        raise HTTPException(404, "Subject not found")
    rows = db.query(Assessment).filter_by(subject_id=subject.id).order_by(Assessment.assessment_date, Assessment.name).all()
    return {"assessments": [{"id": a.id, "name": a.name, "max_marks": a.max_marks,
             "assessment_type": a.assessment_type} for a in rows]}


@router.get("/api/faculty/class-intelligence")
def class_intelligence(subject_id: int, section: str, user: User = Depends(require_faculty), db: Session = Depends(get_db)):
    faculty = _faculty(db, user)
    subject = db.query(Subject).filter_by(id=subject_id, department_id=faculty.department_id).first()
    if not subject:
        raise HTTPException(404, "Subject not found")
    roster = db.query(Student).join(Enrollment, Enrollment.student_id == Student.id).filter(
        Enrollment.subject_id == subject.id, Student.semester == subject.semester, Student.section == section).all()
    assessment_ids = [a.id for a in db.query(Assessment).filter_by(subject_id=subject.id).all()]
    results = []
    for s in roster:
        attendance = db.query(AttendanceRecord.status).join(AttendanceSession).filter(
            AttendanceSession.subject_id == subject.id, AttendanceSession.section == section,
            AttendanceRecord.student_id == s.id).all()
        present = sum(str(x[0]).upper() == "PRESENT" for x in attendance)
        att_pct = round(100 * present / len(attendance), 2) if attendance else None
        marks = db.query(Mark.marks_obtained, Assessment.max_marks).join(Assessment).filter(
            Mark.student_id == s.id, Assessment.subject_id == subject.id).all()
        average = round(100 * sum(m for m, _ in marks) / sum(mx for _, mx in marks), 2) if marks and sum(mx for _, mx in marks) else None
        results.append({"student": s.name, "register_number": s.register_number, "attendance": att_pct,
                        "average_marks": average, "attention": "REVIEW" if (att_pct is not None and att_pct < 75) or (average is not None and average < 40) else "OK"})
    observed_att = [x["attendance"] for x in results if x["attendance"] is not None]
    observed_marks = [x["average_marks"] for x in results if x["average_marks"] is not None]
    return {"subject": subject.name, "section": section, "student_count": len(roster),
            "attendance_average": round(sum(observed_att)/len(observed_att), 2) if observed_att else None,
            "assessment_average": round(sum(observed_marks)/len(observed_marks), 2) if observed_marks else None,
            "highest": max(observed_marks) if observed_marks else None,
            "lowest": min(observed_marks) if observed_marks else None,
            "students": results}


class AdminStudentCreate(BaseModel):
    register_number: str = Field(min_length=3, max_length=50)
    name: str = Field(min_length=1, max_length=150)
    department_id: int
    year_of_study: int = Field(ge=1, le=4)
    semester: int = Field(ge=1, le=8)
    section: str = Field(min_length=1, max_length=20)
    academic_year: str = Field(min_length=4, max_length=20)
    username: str = Field(min_length=3, max_length=100)
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=12, max_length=128)


@router.get("/api/admin/departments")
def admin_departments(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return {"departments": [{"id": d.id, "code": d.code, "name": d.name}
            for d in db.query(Department).order_by(Department.name).all()]}


@router.post("/api/admin/students", status_code=201)
def create_admin_student(data: AdminStudentCreate, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    register_number, username, email = data.register_number.strip(), data.username.strip().lower(), data.email.strip().lower()
    name, section = data.name.strip(), data.section.strip().upper()
    if data.semester not in (data.year_of_study * 2 - 1, data.year_of_study * 2):
        raise HTTPException(422, "Semester must match the selected year of study")
    department = db.query(Department).filter_by(id=data.department_id).first()
    if not department:
        raise HTTPException(404, "Department not found")
    if not name or not register_number or not section:
        raise HTTPException(422, "Name, student ID, and section are required")
    duplicate = db.query(Student).filter_by(register_number=register_number).first()
    if duplicate or db.query(User).filter((User.username == username) | (User.email == email)).first():
        raise HTTPException(409, "Student ID, username, or email is already in use")
    student_user = User(username=username, email=email, password_hash=hash_password(data.password), role="STUDENT", is_active=True)
    db.add(student_user)
    db.flush()
    student = Student(user_id=student_user.id, register_number=register_number, name=name,
                      department_id=department.id, batch=data.academic_year.strip(), semester=data.semester,
                      section=section)
    db.add(student)
    db.flush()
    subjects = db.query(Subject).filter_by(department_id=department.id, semester=data.semester).all()
    for subject in subjects:
        db.add(Enrollment(student_id=student.id, subject_id=subject.id, academic_year=data.academic_year.strip()))
    _audit(db, user.id, "STUDENT_CREATED", "Student", student.id,
           {"register_number": register_number, "name": name, "department": department.name,
            "year_of_study": data.year_of_study, "semester": data.semester, "section": section,
            "academic_year": data.academic_year.strip(), "enrolled_subjects": len(subjects)})
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"student": {"register_number": register_number, "name": name, "department": department.name,
                        "semester": data.semester, "section": section, "username": username,
                        "enrolled_subjects": len(subjects)}}


@router.get("/api/admin/overview")
def admin_overview(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    counts = lambda model: db.query(func.count(model.id)).scalar() or 0
    pending_achievements = db.query(func.count(Achievement.id)).filter_by(verification_status="PENDING").scalar() or 0
    pending_requests = db.query(func.count(MentorRequest.id)).filter_by(status="PENDING").scalar() or 0
    logs = db.query(AuditLog, User).outerjoin(User, User.id == AuditLog.user_id).order_by(AuditLog.created_at.desc()).limit(50).all()
    return {"counts": {"students": counts(Student), "faculty": counts(Faculty), "subjects": counts(Subject),
             "departments": counts(Department), "resources": counts(Resource), "achievements": counts(Achievement),
             "pending_achievement_reviews": pending_achievements, "pending_mentor_requests": pending_requests,
             "attendance_sessions": counts(AttendanceSession), "assessments": counts(Assessment)},
            "audit_activity": [{"timestamp": a.created_at, "user": u.username if u else None,
             "action": a.action, "entity": a.entity_type, "entity_id": a.entity_id, "details": a.details} for a, u in logs]}


@router.get("/api/admin/students")
def admin_students(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    students = db.query(Student).order_by(Student.register_number).all()
    output = []
    for s in students:
        rows = db.query(AttendanceRecord.status).filter_by(student_id=s.id).all()
        present = sum(str(r[0]).upper() == "PRESENT" for r in rows)
        output.append({"register_number": s.register_number, "name": s.name, "department": s.department.name,
                       "semester": s.semester, "section": s.section,
                       "attendance": round(100*present/len(rows), 2) if rows else None,
                       "cgpa": s.cgpa, "status": "ACTIVE" if s.user.is_active else "INACTIVE"})
    return {"students": output}
