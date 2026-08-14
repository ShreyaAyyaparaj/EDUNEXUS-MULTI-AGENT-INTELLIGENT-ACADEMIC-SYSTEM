from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.db.session import Base

class UserRole(str, enum.Enum):
    STUDENT = "student"
    FACULTY = "faculty"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False, default=UserRole.STUDENT)
    department_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("departments.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    department = relationship("Department", back_populates="users")
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False, foreign_keys="StudentProfile.user_id")
    faculty_profile = relationship("FacultyProfile", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")

class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    users = relationship("User", back_populates="department")
    courses = relationship("Course", back_populates="department")
    students = relationship("StudentProfile", back_populates="department")

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    roll_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    semester: Mapped[int] = mapped_column(Integer, default=6)
    cgpa: Mapped[float] = mapped_column(Float, default=8.0)
    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.id"), nullable=False)
    advisor_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    user = relationship("User", foreign_keys=[user_id], back_populates="student_profile")
    advisor = relationship("User", foreign_keys=[advisor_id])
    department = relationship("Department", back_populates="students")
    attendances = relationship("Attendance", back_populates="student")
    marks = relationship("Mark", back_populates="student")
    submissions = relationship("AssignmentSubmission", back_populates="student")
    skillfolios = relationship("SkillFolio", back_populates="student")
    mentor_requests = relationship("MentorRequest", back_populates="student")
    placement_record = relationship("PlacementRecord", back_populates="student", uselist=False)

class FacultyProfile(Base):
    __tablename__ = "faculty_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    designation: Mapped[str] = mapped_column(String(100), default="Assistant Professor")
    research_interests: Mapped[str] = mapped_column(Text, default="Machine Learning, Data Science")
    bio: Mapped[str] = mapped_column(Text, default="Faculty member with extensive academic experience.")
    is_available_for_mentorship: Mapped[bool] = mapped_column(Boolean, default=True)

    user = relationship("User", back_populates="faculty_profile")
    mentor_requests = relationship("MentorRequest", back_populates="faculty")

class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.id"), nullable=False)
    semester: Mapped[int] = mapped_column(Integer, default=6)
    credits: Mapped[int] = mapped_column(Integer, default=4)

    department = relationship("Department", back_populates="courses")
    attendances = relationship("Attendance", back_populates="course")
    marks = relationship("Mark", back_populates="course")
    assignments = relationship("Assignment", back_populates="course")

class Attendance(Base):
    __tablename__ = "attendances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"), nullable=False)
    date: Mapped[str] = mapped_column(String(20), nullable=False) # YYYY-MM-DD
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="present") # present / absent

    student = relationship("StudentProfile", back_populates="attendances")
    course = relationship("Course", back_populates="attendances")

class Mark(Base):
    __tablename__ = "marks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"), nullable=False)
    exam_type: Mapped[str] = mapped_column(String(50), nullable=False) # internal1, internal2, end_sem
    score: Mapped[float] = mapped_column(Float, nullable=False)
    max_score: Mapped[float] = mapped_column(Float, default=100.0)

    student = relationship("StudentProfile", back_populates="marks")
    course = relationship("Course", back_populates="marks")

class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    due_date: Mapped[str] = mapped_column(String(50), nullable=False)
    max_score: Mapped[float] = mapped_column(Float, default=100.0)

    course = relationship("Course", back_populates="assignments")
    submissions = relationship("AssignmentSubmission", back_populates="assignment")

class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    assignment_id: Mapped[int] = mapped_column(Integer, ForeignKey("assignments.id"), nullable=False)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending") # submitted, pending, graded
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("StudentProfile", back_populates="submissions")

class SkillFolio(Base):
    __tablename__ = "skillfolios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False) # certification, project, paper
    issuing_body: Mapped[str] = mapped_column(String(255), nullable=False)
    verified_by_faculty_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="verified") # pending, verified

    student = relationship("StudentProfile", back_populates="skillfolios")

class MentorRequest(Base):
    __tablename__ = "mentor_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    faculty_id: Mapped[int] = mapped_column(Integer, ForeignKey("faculty_profiles.id"), nullable=False)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending") # pending, accepted, rejected
    ai_match_rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student = relationship("StudentProfile", back_populates="mentor_requests")
    faculty = relationship("FacultyProfile", back_populates="mentor_requests")

class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(50), default="general") # risk_alert, mentor_update, general
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")

class AgentExecutionLog(Base):
    __tablename__ = "agent_execution_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    input_summary: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False) # success, fallback, error
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class PlacementRecord(Base):
    __tablename__ = "placement_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    package_lpa: Mapped[float] = mapped_column(Float, nullable=False)
    role: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="placed") # placed, in_process, opted_out
    placement_year: Mapped[int] = mapped_column(Integer, default=2026)

    student = relationship("StudentProfile", back_populates="placement_record")
