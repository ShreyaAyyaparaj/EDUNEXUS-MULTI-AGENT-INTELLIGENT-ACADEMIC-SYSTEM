import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from datetime import date, datetime, timedelta
import hashlib
import random

from app.db.database import SessionLocal
from app.models.entities import (
    User,
    Department,
    Student,
    Faculty,
    Subject,
    Enrollment,
    AttendanceSession,
    AttendanceRecord,
    Assessment,
    Mark,
    SemesterResult,
    Resource,
    Achievement,
    Event,
    Notification,
    AuditLog,
)


# ============================================================
# CONFIG
# ============================================================

random.seed(42)

DB = SessionLocal()

DEPARTMENT_CODE = "CSBS"
DEPARTMENT_NAME = "Computer Science and Business Systems"
BATCH = "2023-2027"

SECTION_A_START = 2116231401103
SECTION_A_END = 2116231401164

SECTION_B_START = 2116231401165
SECTION_B_END = 2116231401225


# ============================================================
# SYNTHETIC NAMES
# ============================================================

FIRST_NAMES = [
    "Aarav", "Aadhya", "Aditya", "Akash", "Ananya",
    "Anirudh", "Arjun", "Ashwin", "Bhavya", "Charan",
    "Dhanush", "Diya", "Harish", "Ishita", "Jeevan",
    "Karthik", "Keerthana", "Krishna", "Lakshmi", "Madhav",
    "Manoj", "Meera", "Nandhini", "Naveen", "Neha",
    "Nikhil", "Pavithra", "Pranav", "Priya", "Rahul",
    "Rakesh", "Riya", "Rohit", "Sanjay", "Sanjana",
    "Saranya", "Shivani", "Shravan", "Siddharth", "Sneha",
    "Sowmya", "Surya", "Swetha", "Tanisha", "Tejas",
    "Varun", "Vignesh", "Vishal", "Yash", "Zoya",
]

LAST_NAMES = [
    "Iyer", "Rajan", "Kumar", "Sharma", "Reddy",
    "Nair", "Krishnan", "Menon", "Balan", "Pillai",
    "Subramanian", "Narayanan", "Prasad", "Mohan",
    "Shankar", "Rao", "Patel", "Das", "Joshi", "Mehta",
]


FACULTY_DATA = [
    ("FAC001", "Dr. Anitha Krishnan", "Professor"),
    ("FAC002", "Dr. Karthikeyan Raman", "Associate Professor"),
    ("FAC003", "Dr. Priyanka Menon", "Assistant Professor"),
    ("FAC004", "Dr. Suresh Narayanan", "Assistant Professor"),
    ("FAC005", "Dr. Meenakshi Rao", "Associate Professor"),
]


# ============================================================
# SUBJECT DATA
# ============================================================

SUBJECT_DATA = [

    # Semester 1
    ("HS23111", "Professional English", 1, 3),
    ("MA23111", "Discrete Mathematics", 1, 4),
    ("PH23111", "Engineering Physics", 1, 3),
    ("CY23111", "Engineering Chemistry", 1, 3),
    ("GE23111", "Engineering Graphics", 1, 3),
    ("CS23111", "Programming in C", 1, 4),

    # Semester 2
    ("MA23211", "Probability and Statistics", 2, 4),
    ("CS23211", "Data Structures", 2, 4),
    ("CS23212", "Object Oriented Programming", 2, 3),
    ("EC23211", "Digital Electronics", 2, 3),
    ("CS23213", "Database Management Systems", 2, 4),
    ("CS23214", "Web Programming", 2, 3),

    # Semester 3
    ("CS23311", "Operating Systems", 3, 4),
    ("CS23312", "Computer Networks", 3, 4),
    ("CS23313", "Design and Analysis of Algorithms", 3, 4),
    ("CS23314", "Artificial Intelligence", 3, 3),
    ("CB23311", "Business Analytics", 3, 3),

    # Semester 4
    ("CS23411", "Machine Learning", 4, 4),
    ("CS23412", "Software Engineering", 4, 3),
    ("CS23413", "Computer Architecture", 4, 3),
    ("CS23414", "Data Mining", 4, 4),
    ("CB23411", "Business Intelligence", 4, 3),

    # Semester 5
    ("CB23E32", "Fundamentals of IoT", 5, 4),
    ("CB23621", "Internship", 5, 2),

    # Semester 6
    ("BA23613", "Business Ethics", 6, 3),
    ("CS23611", "Cloud Computing", 6, 4),
    ("CS23612", "Big Data Analytics", 6, 4),
    ("CS23613", "Deep Learning", 6, 4),

    # Semester 7 - current
    ("CB23E36", "Cryptology", 7, 4),
    ("CB23731", "Data Visualization Techniques", 7, 3),
    ("CB23732", "IT Project Management", 7, 3),
    ("NPTEL-MSID", "Managerial Skills for Interpersonal Development", 7, 3),
    ("CB23721", "Project Evaluation I", 7, 2),
]


# ============================================================
# HELPERS
# ============================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def academic_year(semester):
    years = {
        1: "2023-24",
        2: "2023-24",
        3: "2024-25",
        4: "2024-25",
        5: "2025-26",
        6: "2025-26",
        7: "2026-27",
    }

    return years[semester]


def student_name(index):
    first = FIRST_NAMES[(index - 1) % len(FIRST_NAMES)]
    last = LAST_NAMES[
        ((index - 1) // len(FIRST_NAMES)) % len(LAST_NAMES)
    ]

    return f"{first} {last}"


# ============================================================
# CLEAR DATABASE
# ============================================================

def clear_database():

    print("Clearing existing development data...")

    # Children first
    DB.query(AuditLog).delete()
    DB.query(Notification).delete()
    DB.query(Achievement).delete()
    DB.query(Resource).delete()

    DB.query(AttendanceRecord).delete()
    DB.query(AttendanceSession).delete()

    DB.query(Mark).delete()
    DB.query(Assessment).delete()

    DB.query(Enrollment).delete()
    DB.query(SemesterResult).delete()

    DB.query(Event).delete()

    DB.query(Student).delete()
    DB.query(Faculty).delete()
    DB.query(Subject).delete()
    DB.query(Department).delete()
    DB.query(User).delete()

    DB.commit()


# ============================================================
# DEPARTMENT
# ============================================================

def create_department():

    department = Department(
        code=DEPARTMENT_CODE,
        name=DEPARTMENT_NAME,
    )

    DB.add(department)
    DB.flush()

    return department.id


# ============================================================
# FACULTY
# ============================================================

def create_faculty(department_id):

    faculty_ids = []

    for employee_id, name, designation in FACULTY_DATA:

        user = User(
            username=employee_id.lower(),
            email=f"{employee_id.lower()}@edunexus.edu",
            password_hash=hash_password("EduNexus@123"),
            role="FACULTY",
            is_active=True,
        )

        DB.add(user)
        DB.flush()

        faculty = Faculty(
            user_id=user.id,
            employee_id=employee_id,
            name=name,
            department_id=department_id,
            designation=designation,
        )

        DB.add(faculty)
        DB.flush()

        faculty_ids.append(faculty.id)

    return faculty_ids


# ============================================================
# SUBJECTS
# ============================================================

def create_subjects(department_id):

    subject_ids = {}

    for code, name, semester, credits in SUBJECT_DATA:

        subject = Subject(
            code=code,
            name=name,
            department_id=department_id,
            semester=semester,
            credits=credits,
        )

        DB.add(subject)
        DB.flush()

        subject_ids[code] = subject.id

    return subject_ids


# ============================================================
# STUDENTS
# ============================================================

def create_students(department_id):

    students = []

    register_numbers = (
        list(range(SECTION_A_START, SECTION_A_END + 1))
        +
        list(range(SECTION_B_START, SECTION_B_END + 1))
    )

    for index, register_number in enumerate(
        register_numbers,
        start=1,
    ):

        if register_number <= SECTION_A_END:
            section = "A"
        else:
            section = "B"

        profile = index % 10

        if profile in (0, 1):
            performance = 88
            attendance = 92

        elif profile in (2, 3):
            performance = 76
            attendance = 85

        elif profile in (4, 5, 6, 7):
            performance = 67
            attendance = 78

        elif profile == 8:
            performance = 48
            attendance = 62

        else:
            performance = 58
            attendance = 70

        username = f"student{index:03d}"

        user = User(
            username=username,
            email=f"{username}@edunexus.edu",
            password_hash=hash_password("EduNexus@123"),
            role="STUDENT",
            is_active=True,
        )

        DB.add(user)
        DB.flush()

        student = Student(
            user_id=user.id,
            register_number=str(register_number),
            name=student_name(index),
            department_id=department_id,
            batch=BATCH,
            semester=7,
            section=section,
            cgpa=None,
        )

        DB.add(student)
        DB.flush()

        students.append({
            "id": student.id,
            "user_id": user.id,
            "register_number": str(register_number),
            "section": section,
            "performance": performance,
            "attendance": attendance,
            "profile": profile,
        })

    return students


# ============================================================
# ENROLLMENTS
# ============================================================

def create_enrollments(students, subject_ids):

    print("Creating enrollments...")

    for student in students:

        for code, subject_id in subject_ids.items():

            semester = next(
                semester
                for subject_code, _, semester, _ in SUBJECT_DATA
                if subject_code == code
            )

            DB.add(
                Enrollment(
                    student_id=student["id"],
                    subject_id=subject_id,
                    academic_year=academic_year(semester),
                )
            )

    DB.flush()


# ============================================================
# SEMESTER RESULTS
# ============================================================

def create_semester_results(students):

    print("Creating Semester 1-6 results...")

    credits = {
        1: 22,
        2: 23,
        3: 22,
        4: 22,
        5: 21,
        6: 22,
    }

    for student in students:

        base = student["performance"]
        profile = student["profile"]

        previous_sgpas = []

        for semester in range(1, 7):

            variation = random.uniform(-4, 4)

            if profile == 9:
                trend = semester * 2.5
            elif profile == 8:
                trend = -semester * 1.0
            else:
                trend = 0

            percentage = clamp(
                base + variation + trend,
                45,
                96,
            )

            sgpa = 5 + ((percentage - 45) / 10)
            sgpa = round(clamp(sgpa, 5.0, 9.8), 2)

            previous_sgpas.append(sgpa)

            cgpa = round(
                sum(previous_sgpas) / len(previous_sgpas),
                2,
            )

            DB.add(
                SemesterResult(
                    student_id=student["id"],
                    semester=semester,
                    sgpa=sgpa,
                    cgpa=cgpa,
                    total_credits=credits[semester],
                    academic_year=academic_year(semester),
                )
            )

        # Update current Student.cgpa with Sem 6 cumulative CGPA.
        student_db = DB.get(Student, student["id"])

        if student_db:
            student_db.cgpa = cgpa

    DB.flush()


# ============================================================
# ASSESSMENTS
# ============================================================

def create_assessments(subject_ids):

    print("Creating assessments...")

    assessments = []

    for code, subject_id in subject_ids.items():

        semester = next(
            semester
            for subject_code, _, semester, _ in SUBJECT_DATA
            if subject_code == code
        )

        # Historical Sem 1-6
        if semester <= 6:

            specs = [
                ("CAT-I", "CAT", 50),
                ("CAT-II", "CAT", 50),
                ("Model Examination", "MODEL", 100),
            ]

            for name, assessment_type, max_marks in specs:

                assessment = Assessment(
                    subject_id=subject_id,
                    name=name,
                    assessment_type=assessment_type,
                    max_marks=max_marks,
                    assessment_date=date(
                        2025,
                        min(semester + 1, 12),
                        10,
                    ),
                )

                DB.add(assessment)
                DB.flush()

                assessments.append({
                    "id": assessment.id,
                    "subject_id": subject_id,
                    "semester": semester,
                    "max_marks": max_marks,
                })

        # Current Sem 7
        elif semester == 7:

            # NPTEL credit transfer -> no fabricated marks.
            if code == "NPTEL-MSID":
                continue

            if code == "CB23721":

                specs = [
                    ("Project Evaluation I", "PROJECT", 100),
                ]

            else:

                specs = [
                    ("CAT-I", "CAT", 50),
                    ("Internal Assessment", "INTERNAL", 50),
                ]

            for name, assessment_type, max_marks in specs:

                assessment = Assessment(
                    subject_id=subject_id,
                    name=name,
                    assessment_type=assessment_type,
                    max_marks=max_marks,
                    assessment_date=date(2026, 9, 10),
                )

                DB.add(assessment)
                DB.flush()

                assessments.append({
                    "id": assessment.id,
                    "subject_id": subject_id,
                    "semester": semester,
                    "max_marks": max_marks,
                })

    return assessments


# ============================================================
# MARKS
# ============================================================

def create_marks(students, assessments):

    print("Creating marks...")

    for assessment in assessments:

        for student in students:

            base = student["performance"]
            profile = student["profile"]

            variation = random.uniform(-12, 12)

            if profile == 9:
                trend = 7
            elif profile == 8:
                trend = -5
            else:
                trend = 0

            percentage = clamp(
                base + variation + trend,
                25,
                98,
            )

            marks = round(
                assessment["max_marks"] * percentage / 100,
                1,
            )

            DB.add(
                Mark(
                    student_id=student["id"],
                    assessment_id=assessment["id"],
                    marks_obtained=marks,
                )
            )

    DB.flush()


# ============================================================
# ATTENDANCE
# ============================================================

def create_attendance(
    students,
    subject_ids,
    faculty_ids,
):

    print("Creating current Semester 7 attendance...")

    current_subjects = [
        (code, subject_id)
        for code, subject_id in subject_ids.items()
        if next(
            semester
            for subject_code, _, semester, _
            in SUBJECT_DATA
            if subject_code == code
        ) == 7
        and code != "NPTEL-MSID"
    ]

    start_date = date(2026, 8, 3)

    for subject_index, (code, subject_id) in enumerate(
        current_subjects
    ):

        faculty_id = faculty_ids[
            subject_index % len(faculty_ids)
        ]

        for session_number in range(8):

            session_date = start_date + timedelta(
                days=session_number * 7 + subject_index
            )

            if session_date > date.today():
                continue

            period = (session_number % 5) + 1

            for section in ("A", "B"):

                session = AttendanceSession(
                    subject_id=subject_id,
                    faculty_id=faculty_id,
                    session_date=session_date,
                    period=period,
                    semester=7,
                    section=section,
                )

                DB.add(session)
                DB.flush()

                section_students = [
                    student
                    for student in students
                    if student["section"] == section
                ]

                for student in section_students:

                    probability = (
                        student["attendance"] / 100
                    )

                    status = (
                        "PRESENT"
                        if random.random() < probability
                        else "ABSENT"
                    )

                    DB.add(
                        AttendanceRecord(
                            session_id=session.id,
                            student_id=student["id"],
                            status=status,
                        )
                    )

    DB.flush()


# ============================================================
# RESOURCES
# ============================================================

def create_resources(subject_ids, faculty_ids):

    print("Creating academic resources...")

    resources = [
        ("CB23E36", "Cryptology Fundamentals"),
        ("CB23731", "Data Visualization Notes"),
        ("CB23732", "IT Project Management Guide"),
        ("CB23721", "Project Evaluation Guidelines"),
        ("CS23611", "Cloud Computing Notes"),
        ("CS23612", "Big Data Analytics Notes"),
        ("CS23613", "Deep Learning Study Material"),
    ]

    for index, (subject_code, title) in enumerate(resources):

        if subject_code not in subject_ids:
            continue

        DB.add(
            Resource(
                subject_id=subject_ids[subject_code],
                faculty_id=faculty_ids[index % len(faculty_ids)],
                title=title,
                description=f"Academic resource for {title}.",
                file_name=f"{subject_code.lower()}_notes.pdf",
                file_path=f"resources/{subject_code.lower()}_notes.pdf",
                resource_type="PDF",
            )
        )

    DB.flush()


# ============================================================
# ACHIEVEMENTS
# ============================================================

def create_achievements(students):

    print("Creating achievements...")

    templates = [
        (
            "Hackathon Participation",
            "HACKATHON",
            "Participated in an inter-college technology hackathon.",
        ),
        (
            "Python Workshop",
            "WORKSHOP",
            "Completed a technical workshop on Python and data science.",
        ),
        (
            "Technical Symposium",
            "COMPETITION",
            "Participated in a technical symposium.",
        ),
        (
            "Student Club Leadership",
            "LEADERSHIP",
            "Contributed to student club activities.",
        ),
        (
            "Industry Internship",
            "INTERNSHIP",
            "Completed an industry internship.",
        ),
    ]

    for index, student in enumerate(students):

        if index % 3 != 0:
            continue

        title, category, description = templates[
            (index // 3) % len(templates)
        ]

        status = (
            "VERIFIED"
            if index % 2 == 0
            else "PENDING"
        )

        DB.add(
            Achievement(
                student_id=student["id"],
                title=title,
                category=category,
                description=description,
                verification_status=status,
            )
        )

    DB.flush()


# ============================================================
# EVENTS
# ============================================================

def create_events():

    print("Creating events...")

    DB.add_all([
        Event(
            title="EduNexus Academic Orientation",
            description="Academic orientation and student support session.",
            event_date=datetime(2026, 9, 15, 10, 0),
            location="Seminar Hall",
        ),
        Event(
            title="AI and Data Science Workshop",
            description="Hands-on AI and data science workshop.",
            event_date=datetime(2026, 9, 20, 14, 0),
            location="Innovation Lab",
        ),
        Event(
            title="Project Review Session",
            description="Semester project review session.",
            event_date=datetime(2026, 9, 22, 10, 0),
            location="Project Lab",
        ),
    ])

    DB.flush()


# ============================================================
# NOTIFICATIONS
# ============================================================

def create_notifications(students):

    print("Creating notifications...")

    for student in students:

        if int(student["register_number"][-2:]) % 5 != 0:
            continue

        DB.add(
            Notification(
                user_id=student["user_id"],
                title="Attendance Reminder",
                message=(
                    "Review your current semester attendance "
                    "and maintain the required attendance percentage."
                ),
                is_read=False,
            )
        )

    DB.flush()


# ============================================================
# AUDIT LOGS
# ============================================================

def create_audit_logs(faculty_ids):

    print("Creating audit logs...")

    for faculty_id in faculty_ids:

        faculty = DB.get(Faculty, faculty_id)

        DB.add(
            AuditLog(
                user_id=faculty.user_id,
                action="SEED_INITIALIZATION",
                entity_type="SYSTEM",
                entity_id=None,
                details="Synthetic EduNexus development dataset initialized.",
            )
        )

    DB.flush()


# ============================================================
# VERIFICATION
# ============================================================

def print_summary():

    print()
    print("=" * 60)
    print("SEED COMPLETED SUCCESSFULLY")
    print("=" * 60)

    print(f"Users          : {DB.query(User).count()}")
    print(f"Departments    : {DB.query(Department).count()}")
    print(f"Students       : {DB.query(Student).count()}")
    print(f"Faculty        : {DB.query(Faculty).count()}")
    print(f"Subjects       : {DB.query(Subject).count()}")
    print(f"Enrollments    : {DB.query(Enrollment).count()}")
    print(f"Assessments    : {DB.query(Assessment).count()}")
    print(f"Marks          : {DB.query(Mark).count()}")
    print(f"Attendance     : {DB.query(AttendanceRecord).count()}")
    print(f"Results        : {DB.query(SemesterResult).count()}")
    print(f"Resources      : {DB.query(Resource).count()}")
    print(f"Achievements   : {DB.query(Achievement).count()}")
    print(f"Events         : {DB.query(Event).count()}")
    print(f"Notifications  : {DB.query(Notification).count()}")
    print(f"Audit Logs     : {DB.query(AuditLog).count()}")

    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("EDUNEXUS DATABASE SEED")
    print("=" * 60)

    try:

        clear_database()

        department_id = create_department()

        faculty_ids = create_faculty(
            department_id
        )

        subject_ids = create_subjects(
            department_id
        )

        students = create_students(
            department_id
        )

        create_enrollments(
            students,
            subject_ids
        )

        create_semester_results(
            students
        )

        assessments = create_assessments(
            subject_ids
        )

        create_marks(
            students,
            assessments
        )

        create_attendance(
            students,
            subject_ids,
            faculty_ids
        )

        create_resources(
            subject_ids,
            faculty_ids
        )

        create_achievements(
            students
        )

        create_events()

        create_notifications(
            students
        )

        create_audit_logs(
            faculty_ids
        )

        DB.commit()

        print_summary()

    except Exception as error:

        DB.rollback()

        print()
        print("=" * 60)
        print("SEED FAILED")
        print("=" * 60)
        print(type(error).__name__)
        print(str(error))
        print("=" * 60)

        raise

    finally:
        DB.close()


if __name__ == "__main__":
    main()
