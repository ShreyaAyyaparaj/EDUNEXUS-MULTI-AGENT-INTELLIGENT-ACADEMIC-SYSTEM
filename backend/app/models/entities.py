from datetime import datetime, date

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint,
)

from sqlalchemy.orm import relationship

from app.db.database import Base


# =========================================================
# USERS
# =========================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# =========================================================
# DEPARTMENTS
# =========================================================

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(150), nullable=False)

    students = relationship("Student", back_populates="department")
    faculty = relationship("Faculty", back_populates="department")


# =========================================================
# STUDENTS
# =========================================================

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )

    register_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    name = Column(String(150), nullable=False)

    department_id = Column(
        Integer,
        ForeignKey("departments.id"),
        nullable=False,
    )

    batch = Column(String(20), nullable=False)
    semester = Column(Integer, nullable=False)
    section = Column(String(20), nullable=False)

    cgpa = Column(Float, nullable=True)

    user = relationship("User")
    department = relationship("Department", back_populates="students")

    enrollments = relationship(
        "Enrollment",
        back_populates="student",
        cascade="all, delete-orphan",
    )

    attendance_records = relationship(
        "AttendanceRecord",
        back_populates="student",
    )

    marks = relationship(
        "Mark",
        back_populates="student",
    )


# =========================================================
# FACULTY
# =========================================================

class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )

    employee_id = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    name = Column(String(150), nullable=False)

    department_id = Column(
        Integer,
        ForeignKey("departments.id"),
        nullable=False,
    )

    designation = Column(String(100))

    user = relationship("User")

    department = relationship(
        "Department",
        back_populates="faculty",
    )


# =========================================================
# SUBJECTS
# =========================================================

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True)

    code = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    name = Column(String(150), nullable=False)

    department_id = Column(
        Integer,
        ForeignKey("departments.id"),
        nullable=False,
    )

    semester = Column(Integer, nullable=False)
    credits = Column(Integer, nullable=True)

    enrollments = relationship(
        "Enrollment",
        back_populates="subject",
    )


# =========================================================
# ENROLLMENTS
# =========================================================

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True)

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False,
    )

    subject_id = Column(
        Integer,
        ForeignKey("subjects.id"),
        nullable=False,
    )

    academic_year = Column(String(20), nullable=False)

    student = relationship(
        "Student",
        back_populates="enrollments",
    )

    subject = relationship(
        "Subject",
        back_populates="enrollments",
    )

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "subject_id",
            "academic_year",
            name="uq_student_subject_year",
        ),
    )


# =========================================================
# ATTENDANCE SESSION
# =========================================================

class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    id = Column(Integer, primary_key=True)

    subject_id = Column(
        Integer,
        ForeignKey("subjects.id"),
        nullable=False,
    )

    faculty_id = Column(
        Integer,
        ForeignKey("faculty.id"),
        nullable=False,
    )

    session_date = Column(Date, nullable=False)
    period = Column(Integer, nullable=False)

    semester = Column(Integer, nullable=False)
    section = Column(String(20), nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    records = relationship(
        "AttendanceRecord",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "subject_id",
            "session_date",
            "period",
            "section",
            name="uq_attendance_session",
        ),
    )


# =========================================================
# ATTENDANCE RECORD
# =========================================================

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True)

    session_id = Column(
        Integer,
        ForeignKey("attendance_sessions.id"),
        nullable=False,
    )

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False,
    )

    status = Column(
        String(20),
        nullable=False,
    )

    marked_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    session = relationship(
        "AttendanceSession",
        back_populates="records",
    )

    student = relationship(
        "Student",
        back_populates="attendance_records",
    )

    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "student_id",
            name="uq_attendance_student_session",
        ),
    )


# =========================================================
# ASSESSMENTS
# =========================================================

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True)

    subject_id = Column(
        Integer,
        ForeignKey("subjects.id"),
        nullable=False,
    )

    name = Column(String(100), nullable=False)

    assessment_type = Column(
        String(50),
        nullable=False,
    )

    max_marks = Column(
        Float,
        nullable=False,
    )

    assessment_date = Column(Date, nullable=True)


# =========================================================
# MARKS
# =========================================================

class Mark(Base):
    __tablename__ = "marks"

    id = Column(Integer, primary_key=True)

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False,
    )

    assessment_id = Column(
        Integer,
        ForeignKey("assessments.id"),
        nullable=False,
    )

    marks_obtained = Column(
        Float,
        nullable=False,
    )

    student = relationship(
        "Student",
        back_populates="marks",
    )

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "assessment_id",
            name="uq_student_assessment",
        ),
    )


# =========================================================
# SEMESTER RESULTS
# =========================================================

class SemesterResult(Base):
    __tablename__ = "semester_results"

    id = Column(Integer, primary_key=True)

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False,
    )

    semester = Column(Integer, nullable=False)

    sgpa = Column(Float)
    cgpa = Column(Float)

    total_credits = Column(Integer)

    academic_year = Column(String(20))

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "semester",
            "academic_year",
            name="uq_student_semester_result",
        ),
    )


# =========================================================
# RESOURCES
# =========================================================

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True)

    subject_id = Column(
        Integer,
        ForeignKey("subjects.id"),
        nullable=False,
    )

    faculty_id = Column(
        Integer,
        ForeignKey("faculty.id"),
        nullable=False,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    description = Column(Text)

    file_name = Column(String(255))
    file_path = Column(String(500))

    resource_type = Column(
        String(50),
        nullable=True,
    )

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow,
    )


# =========================================================
# ACHIEVEMENTS
# =========================================================

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True)

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False,
    )

    title = Column(String(255), nullable=False)
    category = Column(String(100))
    description = Column(Text)
    achievement_date = Column(Date, nullable=True)
    certificate_name = Column(String(255), nullable=True)
    certificate_path = Column(String(500), nullable=True)
    faculty_message = Column(Text, nullable=True)
    reviewed_by = Column(Integer, ForeignKey("faculty.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    verification_status = Column(
        String(30),
        default="PENDING",
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )


class MentorRequest(Base):
    __tablename__ = "mentor_requests"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    faculty_id = Column(Integer, ForeignKey("faculty.id"), nullable=False, index=True)
    project_domain = Column(String(200), nullable=False)
    query = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(30), nullable=False, default="PENDING", index=True)
    faculty_message = Column(Text, nullable=True)
    email_status = Column(String(30), nullable=False, default="NOT_CONFIGURED")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# =========================================================
# EVENTS
# =========================================================

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)

    title = Column(String(255), nullable=False)
    description = Column(Text)

    event_date = Column(DateTime)
    location = Column(String(255))

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )


# =========================================================
# NOTIFICATIONS
# =========================================================

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    is_read = Column(Boolean, default=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )


# =========================================================
# AUDIT LOG
# =========================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    action = Column(
        String(100),
        nullable=False,
    )

    entity_type = Column(String(100))
    entity_id = Column(String(100))

    details = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )
