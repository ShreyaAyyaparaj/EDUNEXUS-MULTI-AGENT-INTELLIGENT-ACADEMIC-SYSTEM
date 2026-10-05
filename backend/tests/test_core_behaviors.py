import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agents.router import classify_question
from app.models.entities import Achievement, MentorRequest
from app.schemas.attendance import AttendanceRequest


class RouterTests(unittest.TestCase):
    def test_personal_attendance_uses_student_success(self):
        self.assertEqual(classify_question("What is my attendance?"), "student_success")

    def test_policy_uses_university_route(self):
        self.assertEqual(classify_question("Explain the mentor-mentee policy"), "university")

    def test_faculty_low_attendance_uses_intelligence_route(self):
        self.assertEqual(classify_question("Which students have low attendance?", "FACULTY"), "faculty_intelligence")

    def test_curriculum_question_uses_academic_route(self):
        self.assertEqual(classify_question("What subjects are in Semester VII?"), "academic")


class AcademicSchemaTests(unittest.TestCase):
    def test_attendance_normalizes_identifiers(self):
        request = AttendanceRequest(subject_code=" cb23721 ", date=date(2026, 9, 28), period=1,
                                    section=" a ", absent_student_ids=[" 123 "])
        self.assertEqual(request.subject_code, "CB23721")
        self.assertEqual(request.section, "A")
        self.assertEqual(request.absent_student_ids, ["123"])

    def test_attendance_rejects_duplicate_absent_students(self):
        with self.assertRaises(ValueError):
            AttendanceRequest(subject_code="CB23721", date=date(2026, 9, 28), period=1,
                              section="A", absent_student_ids=["123", "123"])

    def test_existing_achievement_entity_was_extended(self):
        self.assertIn("faculty_message", Achievement.__table__.columns)
        self.assertIn("certificate_path", Achievement.__table__.columns)
        self.assertIn("reviewed_by", Achievement.__table__.columns)

    def test_mentor_request_has_state_and_email_status(self):
        self.assertIn("status", MentorRequest.__table__.columns)
        self.assertIn("email_status", MentorRequest.__table__.columns)


if __name__ == "__main__":
    unittest.main()
