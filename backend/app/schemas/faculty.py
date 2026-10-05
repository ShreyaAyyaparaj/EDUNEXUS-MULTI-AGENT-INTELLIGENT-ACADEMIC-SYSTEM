from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AtRiskStudent(BaseModel):
    student_id: int
    user_id: int
    name: str
    roll_number: str
    department: str
    semester: int
    attendance_percentage: float
    marks_average: float
    unsubmitted_assignments: int
    risk_level: str # High, Medium
    ai_risk_narrative: str
    intervention_recommendation: str

class MentorRequestAction(BaseModel):
    request_id: int
    status: str # "accepted" or "rejected"

class FacultyAvailabilityUpdate(BaseModel):
    is_available_for_mentorship: bool

class MessageCreate(BaseModel):
    recipient_student_id: int
    title: str
    message: str

class FacultyDashboardResponse(BaseModel):
    faculty_name: str
    department_name: str
    designation: str
    is_available_for_mentorship: bool
    at_risk_students: List[AtRiskStudent]
    pending_mentor_requests: List[dict]
    department_student_count: int
