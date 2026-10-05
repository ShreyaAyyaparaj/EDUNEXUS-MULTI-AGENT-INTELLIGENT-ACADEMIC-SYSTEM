from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import require_faculty
from app.models.all_models import User, FacultyProfile, MentorRequest, StudentProfile, Notification
from app.schemas.faculty import (
    FacultyDashboardResponse, MentorRequestAction, FacultyAvailabilityUpdate, MessageCreate
)
from app.services.erp_service import ERPService
from app.services.pdf_service import PDFService

router = APIRouter(prefix="/faculty", tags=["Faculty ERP"])

@router.get("/dashboard", response_model=FacultyDashboardResponse)
def get_faculty_dashboard(
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db)
):
    data = ERPService.get_faculty_dashboard_data(db, current_user)
    return data

@router.patch("/availability")
def toggle_availability(
    update: FacultyAvailabilityUpdate,
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db)
):
    faculty = db.query(FacultyProfile).filter(FacultyProfile.user_id == current_user.id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found")
    
    faculty.is_available_for_mentorship = update.is_available_for_mentorship
    db.commit()
    return {"status": "success", "is_available_for_mentorship": faculty.is_available_for_mentorship}

@router.post("/mentor-request/action")
def respond_to_mentor_request(
    action: MentorRequestAction,
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db)
):
    req = db.query(MentorRequest).filter(MentorRequest.id == action.request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    req.status = action.status
    db.commit()
    return {"status": "success", "request_id": req.id, "new_status": req.status}

@router.post("/messages")
def send_department_message(
    msg: MessageCreate,
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db)
):
    # Enforce department restriction on backend
    recipient_student = db.query(StudentProfile).filter(StudentProfile.id == msg.recipient_student_id).first()
    if not recipient_student:
        raise HTTPException(status_code=404, detail="Student not found")

    if recipient_student.department_id != current_user.department_id:
        raise HTTPException(
            status_code=403,
            detail="Faculty can only send messages to students within their own department."
        )

    notification = Notification(
        user_id=recipient_student.user_id,
        title=msg.title,
        message=f"From Prof. {current_user.full_name}: {msg.message}",
        type="general",
        is_read=False
    )
    db.add(notification)
    db.commit()
    return {"status": "success", "detail": "Message delivered to student."}

@router.get("/export-report/{student_id}")
def export_student_report(
    student_id: int,
    format: str = "pdf",
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db)
):
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    st_user = student.user
    dash_data = ERPService.get_student_dashboard_data(db, st_user)

    if format.lower() == "csv":
        csv_content = PDFService.generate_student_report_csv(dash_data)
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=student_{student.roll_number}_report.csv"}
        )
    else:
        pdf_bytes = PDFService.generate_student_report_pdf(dash_data)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=student_{student.roll_number}_report.pdf"}
        )
