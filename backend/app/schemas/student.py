from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AttendanceSummary(BaseModel):
    total_classes: int
    present_classes: int
    percentage: float

class CourseMarks(BaseModel):
    course_code: str
    course_name: str
    internal1: Optional[float] = None
    internal2: Optional[float] = None
    end_sem: Optional[float] = None

class AssignmentItem(BaseModel):
    id: int
    course_code: str
    title: str
    due_date: str
    status: str
    score: Optional[float] = None
    max_score: float

class SkillFolioItem(BaseModel):
    id: int
    title: str
    category: str
    issuing_body: str
    status: str

class MentorRequestCreate(BaseModel):
    faculty_id: int
    topic: str
    message: str

class MentorRequestResponse(BaseModel):
    id: int
    faculty_name: str
    topic: str
    message: str
    status: str
    ai_match_rationale: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class StudentDashboardResponse(BaseModel):
    student_name: str
    roll_number: str
    department_name: str
    semester: int
    cgpa: float
    overall_attendance: float
    assignment_completion_rate: float
    attendances_by_course: List[dict]
    marks_summary: List[CourseMarks]
    assignments: List[AssignmentItem]
    skillfolios: List[SkillFolioItem]
    risk_status: str # "good", "warning", "high_risk"
    risk_summary: Optional[str] = None
