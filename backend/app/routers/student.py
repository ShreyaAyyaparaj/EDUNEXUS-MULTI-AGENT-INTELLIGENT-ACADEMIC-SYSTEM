from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import require_student
from app.models.all_models import User, FacultyProfile, MentorRequest, StudentProfile, Notification
from app.schemas.student import StudentDashboardResponse, MentorRequestCreate, MentorRequestResponse
from app.services.erp_service import ERPService

router = APIRouter(prefix="/student", tags=["Student ERP"])

@router.get("/dashboard", response_model=StudentDashboardResponse)
def get_student_dashboard(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    data = ERPService.get_student_dashboard_data(db, current_user)
    return data

@router.post("/mentor-request", response_model=MentorRequestResponse)
def create_mentor_request(
    request: MentorRequestCreate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    student = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    faculty = db.query(FacultyProfile).filter(FacultyProfile.id == request.faculty_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")

    if not faculty.is_available_for_mentorship:
        raise HTTPException(status_code=400, detail="This faculty member is currently unavailable for new mentorship requests.")

    new_req = MentorRequest(
        student_id=student.id,
        faculty_id=faculty.id,
        topic=request.topic,
        message=request.message,
        status="pending",
        ai_match_rationale="Matched based on student research interests and faculty profile."
    )
    db.add(new_req)
    db.commit()
    db.refresh(new_req)

    return MentorRequestResponse(
        id=new_req.id,
        faculty_name=faculty.user.full_name if faculty.user else "Faculty",
        topic=new_req.topic,
        message=new_req.message,
        status=new_req.status,
        ai_match_rationale=new_req.ai_match_rationale,
        created_at=new_req.created_at
    )

@router.delete("/mentor-request/{request_id}")
def delete_mentor_request(
    request_id: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    student = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    req = db.query(MentorRequest).filter(
        MentorRequest.id == request_id,
        MentorRequest.student_id == student.id
    ).first()
    
    if not req:
        raise HTTPException(status_code=404, detail="Mentor request not found or unauthorized")

    db.delete(req)
    db.commit()
    return {"status": "success", "message": f"Mentor request {request_id} deleted successfully."}
