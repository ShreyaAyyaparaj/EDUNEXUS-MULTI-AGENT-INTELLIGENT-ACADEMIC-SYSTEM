import os
import sys
import random
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

from app.db.session import engine, SessionLocal, Base
from app.core.security import get_password_hash
from app.models.all_models import (
    User, UserRole, Department, StudentProfile, FacultyProfile, Course,
    Attendance, Mark, Assignment, AssignmentSubmission, SkillFolio,
    MentorRequest, Notification, PlacementRecord
)

def seed_database():
    print("Initializing EduNexus database schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    print("Seeding Departments...")
    cse = Department(name="Computer Science & Engineering", code="CSE")
    ece = Department(name="Electronics & Communication", code="ECE")
    ai = Department(name="Artificial Intelligence & Data Science", code="AIDS")
    db.add_all([cse, ece, ai])
    db.commit()

    print("Seeding Core Users & Accounts...")
    hashed_pwd = get_password_hash("password123")

    # 1. Admin User
    admin_user = User(
        email="admin@educamp.edu",
        hashed_password=hashed_pwd,
        full_name="Dr. Eleanor Vance (Dean Admin)",
        role=UserRole.ADMIN,
        department_id=cse.id
    )
    db.add(admin_user)

    # 2. Faculty Users
    faculty_users = [
        User(
            email="faculty@educamp.edu",
            hashed_password=hashed_pwd,
            full_name="Dr. Aris Thorne",
            role=UserRole.FACULTY,
            department_id=cse.id
        ),
        User(
            email="prof.sharma@educamp.edu",
            hashed_password=hashed_pwd,
            full_name="Prof. Rajesh Sharma",
            role=UserRole.FACULTY,
            department_id=ai.id
        ),
        User(
            email="dr.chen@educamp.edu",
            hashed_password=hashed_pwd,
            full_name="Dr. Mei Lin Chen",
            role=UserRole.FACULTY,
            department_id=ece.id
        )
    ]
    db.add_all(faculty_users)
    db.commit()

    # Faculty Profiles
    fac_profiles = [
        FacultyProfile(
            user_id=faculty_users[0].id,
            designation="Associate Professor",
            research_interests="Deep Learning, Natural Language Processing, Large Language Models, Multi-Agent Systems",
            bio="Leading researcher in transformer architectures and AI in education.",
            is_available_for_mentorship=True
        ),
        FacultyProfile(
            user_id=faculty_users[1].id,
            designation="Professor & HOD",
            research_interests="Computer Vision, Robotics, Autonomous Vehicles, Edge AI",
            bio="Focuses on real-time object detection and embedded AI deployment.",
            is_available_for_mentorship=True
        ),
        FacultyProfile(
            user_id=faculty_users[2].id,
            designation="Assistant Professor",
            research_interests="VLSI Design, Embedded Systems, IoT, Quantum Computing Hardware",
            bio="Specializes in low-power semiconductor architectures and sensor integration.",
            is_available_for_mentorship=False
        )
    ]
    db.add_all(fac_profiles)
    db.commit()

    print("Seeding Courses...")
    courses = [
        Course(code="CS301", name="Data Structures & Algorithms", department_id=cse.id, semester=6, credits=4),
        Course(code="CS302", name="Database Management Systems", department_id=cse.id, semester=6, credits=4),
        Course(code="CS303", name="Operating Systems & Architecture", department_id=cse.id, semester=6, credits=3),
        Course(code="AI301", name="Deep Learning & Neural Networks", department_id=ai.id, semester=6, credits=4),
        Course(code="EC301", name="Digital Signal Processing", department_id=ece.id, semester=6, credits=3),
    ]
    db.add_all(courses)
    db.commit()

    print("Seeding Student Users & Profiles...")
    # Primary Demo Student
    demo_student_user = User(
        email="student@educamp.edu",
        hashed_password=hashed_pwd,
        full_name="Aarav Sharma",
        role=UserRole.STUDENT,
        department_id=cse.id
    )
    db.add(demo_student_user)
    db.commit()

    demo_student_profile = StudentProfile(
        user_id=demo_student_user.id,
        roll_number="2023CSE042",
        semester=6,
        cgpa=8.85,
        department_id=cse.id,
        advisor_id=faculty_users[0].id
    )
    db.add(demo_student_profile)
    db.commit()

    # Additional Synthetic Students for Class Analytics & At-Risk Scenarios
    synthetic_students_data = [
        ("Rahul Verma", "rahul.v@educamp.edu", "2023CSE015", 6.2, 6, cse.id), # At Risk (Low attendance/marks)
        ("Priya Nair", "priya.n@educamp.edu", "2023CSE089", 9.4, 6, cse.id),
        ("Karan Gupta", "karan.g@educamp.edu", "2023AI007", 7.1, 6, ai.id),
        ("Ananya Roy", "ananya.r@educamp.edu", "2023EC031", 8.1, 6, ece.id),
        ("Vikram Singh", "vikram.s@educamp.edu", "2023CSE102", 5.8, 6, cse.id) # At Risk
    ]

    student_profiles = [demo_student_profile]

    for name, email, roll, cgpa, sem, dept_id in synthetic_students_data:
        u = User(
            email=email,
            hashed_password=hashed_pwd,
            full_name=name,
            role=UserRole.STUDENT,
            department_id=dept_id
        )
        db.add(u)
        db.commit()

        sp = StudentProfile(
            user_id=u.id,
            roll_number=roll,
            semester=sem,
            cgpa=cgpa,
            department_id=dept_id,
            advisor_id=faculty_users[0].id
        )
        db.add(sp)
        db.commit()
        student_profiles.append(sp)

    print("Seeding Attendance Records...")
    # Generate 20 class dates for each student and course
    start_date = datetime.now() - timedelta(days=40)
    for sp in student_profiles:
        # Determine attendance probability based on student performance
        is_low_att = sp.roll_number in ["2023CSE015", "2023CSE102"]
        prob = 0.65 if is_low_att else 0.92

        for course in courses[:3]: # CS courses
            for i in range(20):
                d_str = (start_date + timedelta(days=i*2)).strftime("%Y-%m-%d")
                status = "present" if random.random() < prob else "absent"
                att = Attendance(
                    student_id=sp.id,
                    course_id=course.id,
                    date=d_str,
                    status=status
                )
                db.add(att)
    db.commit()

    print("Seeding Marks Records...")
    for sp in student_profiles:
        is_low_marks = sp.roll_number in ["2023CSE015", "2023CSE102"]
        base = 52.0 if is_low_marks else 85.0

        for course in courses[:3]:
            m1 = Mark(student_id=sp.id, course_id=course.id, exam_type="internal1", score=min(100.0, base + random.uniform(-5, 8)), max_score=100.0)
            m2 = Mark(student_id=sp.id, course_id=course.id, exam_type="internal2", score=min(100.0, base + random.uniform(-8, 5)), max_score=100.0)
            db.add_all([m1, m2])
    db.commit()

    print("Seeding Assignments & Submissions...")
    asg1 = Assignment(course_id=courses[0].id, title="Assignment 1: Dynamic Programming & Graphs", due_date="2026-08-01", max_score=100.0)
    asg2 = Assignment(course_id=courses[1].id, title="Assignment 2: B+ Trees & Query Optimization", due_date="2026-08-10", max_score=100.0)
    asg3 = Assignment(course_id=courses[2].id, title="Assignment 3: Synchronization & Page Replacement", due_date="2026-08-20", max_score=100.0)
    db.add_all([asg1, asg2, asg3])
    db.commit()

    for sp in student_profiles:
        is_at_risk = sp.roll_number in ["2023CSE015", "2023CSE102"]
        
        s1 = AssignmentSubmission(assignment_id=asg1.id, student_id=sp.id, submitted_at=datetime.utcnow(), status="graded", score=88.0 if not is_at_risk else 55.0)
        s2 = AssignmentSubmission(assignment_id=asg2.id, student_id=sp.id, submitted_at=datetime.utcnow(), status="submitted" if not is_at_risk else "pending", score=92.0 if not is_at_risk else None)
        s3 = AssignmentSubmission(assignment_id=asg3.id, student_id=sp.id, submitted_at=None, status="pending", score=None)
        db.add_all([s1, s2, s3])
    db.commit()

    print("Seeding SkillFolios...")
    sf1 = SkillFolio(student_id=demo_student_profile.id, title="Deep Learning Specialization (Coursera)", category="certification", issuing_body="DeepLearning.AI", status="verified")
    sf2 = SkillFolio(student_id=demo_student_profile.id, title="Distributed RAG Search Engine", category="project", issuing_body="GitHub Portfolio", status="verified")
    db.add_all([sf1, sf2])
    db.commit()

    print("Seeding Placement Records...")
    p1 = PlacementRecord(student_id=demo_student_profile.id, company_name="Google", package_lpa=32.5, role="Software Engineer - AI Systems", status="placed", placement_year=2026)
    p2 = PlacementRecord(student_id=student_profiles[2].id, company_name="Microsoft", package_lpa=28.0, role="Software Development Engineer", status="placed", placement_year=2026)
    db.add_all([p1, p2])
    db.commit()

    print("Seeding Initial Notifications...")
    n1 = Notification(user_id=demo_student_user.id, title="Welcome to EduNexus", message="Your academic dashboard is active. Explore your attendance, marks, and mentor discovery.", type="general", is_read=False)
    db.add(n1)
    db.commit()

    db.close()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
