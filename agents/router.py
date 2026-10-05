import sys
from pathlib import Path
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


AgentType = Literal[
    "academic",
    "university",
    "student_success",
    "faculty_intelligence",
]


class AgentState(TypedDict, total=False):
    question: str
    user_id: int
    user_role: str
    route: AgentType
    answer: str
    sources: list


def classify_question(question: str, user_role: str = "STUDENT") -> AgentType:
    q = question.lower().strip()

    if user_role.upper() == "FACULTY" and any(term in q for term in (
        "low attendance", "below attendance", "attendance risk", "students at risk",
    )):
        return "faculty_intelligence"

    student_success_terms = [
        "my attendance",
        "my marks",
        "my score",
        "my result",
        "my performance",
        "my subjects",
        "my semester",
        "my cgpa",
        "my gpa",
        "weak subject",
        "weak subjects",
        "weak in",
        "subjects am i weak",
        "subject am i weak",
        "which subjects am i weak",
        "which subject am i weak",
        "at risk",
        "attendance percentage",
        "how am i doing",
        "how am i performing",
    ]

    university_terms = [
        "college policy",
        "college policies",
        "university policy",
        "university policies",
        "placement policy",
        "placement policies",
        "library policy",
        "library policies",
        "transport policy",
        "transport policies",
        "anti ragging",
        "anti-ragging",
        "grievance",
        "mentor mentee",
        "mentor-mentee",
        "research policy",
        "research policies",
        "e-waste policy",
        "green campus",
        "college contact",
        "admission",
    ]

    if any(term in q for term in student_success_terms):
        return "student_success"

    if any(term in q for term in university_terms):
        return "university"

    return "academic"


def route_question(state: AgentState):
    return {
        "route": classify_question(state["question"], state.get("user_role", "STUDENT"))
    }


def academic_agent(state: AgentState):
    from app.services.rag_service import ask_academic_copilot

    result = ask_academic_copilot(
        question=state["question"],
        top_k=5,
    )

    return {
        "answer": result["answer"],
        "sources": result["sources"],
    }


def university_agent(state: AgentState):
    from app.services.rag_service import ask_academic_copilot

    result = ask_academic_copilot(
        question=state["question"],
        top_k=5,
    )

    return {
        "answer": result["answer"],
        "sources": result["sources"],
    }


def student_success_agent(state: AgentState):
    from app.db.database import SessionLocal
    from app.services.student_success_service import (
        get_student_success_context,
    )

    user_id = state.get("user_id")

    if user_id is None:
        return {
            "answer": "Student identity is required for personalized academic analysis.",
            "sources": [],
        }

    db = SessionLocal()

    try:
        context = get_student_success_context(
            db=db,
            user_id=user_id,
        )

        student = context["student"]
        attendance = context["attendance"]
        marks = context["marks"]
        results = context["results"]

        question = state["question"].lower()

        if "attendance" in question:
            answer = (
                f"Your overall attendance is "
                f"{attendance['overall_percentage']}%.\n\n"
            )

            if attendance["subjects"]:
                answer += "Subject-wise attendance:\n"

                for subject in attendance["subjects"]:
                    answer += (
                        f"- {subject['subject_code']} "
                        f"{subject['subject_name']}: "
                        f"{subject['attendance_percentage']}% "
                        f"({subject['present']}/"
                        f"{subject['total']} present)\n"
                    )

        elif (
            "weak" in question
            or "performance" in question
            or "doing" in question
        ):
            weak_subjects = [
                subject
                for subject in marks
                if subject["percentage"] < 60
            ]

            answer = (
                f"Your academic profile shows "
                f"{len(marks)} assessment records.\n\n"
            )

            if weak_subjects:
                answer += "Assessment records below 60%:\n"

                for item in weak_subjects[:10]:
                    answer += (
                        f"- {item['subject_code']} "
                        f"{item['subject_name']} — "
                        f"{item['assessment']}: "
                        f"{item['percentage']}%\n"
                    )
            else:
                answer += (
                    "No assessment records below 60% "
                    "were found in the current data."
                )

            answer += (
                f"\n\nOverall attendance: "
                f"{attendance['overall_percentage']}%"
            )

        elif "marks" in question or "score" in question:
            answer = (
                f"You currently have "
                f"{len(marks)} assessment records.\n\n"
                "Recent assessment records:\n"
            )

            for item in marks[-10:]:
                answer += (
                    f"- {item['subject_code']} "
                    f"{item['subject_name']} — "
                    f"{item['assessment']}: "
                    f"{item['marks']}/{item['max_marks']} "
                    f"({item['percentage']}%)\n"
                )

        elif "result" in question or "cgpa" in question:
            if results:
                answer = "Your semester results:\n"

                for result in results:
                    answer += (
                        f"- Semester {result['semester']}: "
                        f"SGPA {result['sgpa']}, "
                        f"CGPA {result['cgpa']}\n"
                    )
            else:
                answer = (
                    "No semester results are currently "
                    "available."
                )

        else:
            answer = (
                f"Your current academic profile:\n\n"
                f"- Name: {student['name']}\n"
                f"- Register Number: "
                f"{student['register_number']}\n"
                f"- Semester: {student['semester']}\n"
                f"- Section: {student['section']}\n"
                f"- Overall Attendance: "
                f"{attendance['overall_percentage']}%\n"
                f"- Assessment Records: {len(marks)}\n"
                f"- Semester Results: {len(results)}"
            )

        return {
            "answer": answer,
            "sources": [],
        }

    finally:
        db.close()


def faculty_intelligence_agent(state: AgentState):
    from app.db.database import SessionLocal
    from app.models.entities import AttendanceRecord, AttendanceSession, Faculty, Student
    from sqlalchemy import case, func

    db = SessionLocal()
    try:
        faculty = db.query(Faculty).filter(Faculty.user_id == state.get("user_id")).first()
        if not faculty:
            return {"answer": "Faculty profile is unavailable.", "sources": []}
        rows = db.query(
            Student.name, Student.register_number,
            func.count(AttendanceRecord.id).label("total"),
            func.sum(case((AttendanceRecord.status == "PRESENT", 1), else_=0)).label("present"),
        ).join(AttendanceRecord, AttendanceRecord.student_id == Student.id).join(
            AttendanceSession, AttendanceSession.id == AttendanceRecord.session_id
        ).filter(Student.department_id == faculty.department_id).group_by(
            Student.id, Student.name, Student.register_number
        ).all()
        at_risk = [(name, reg, round(100 * (present or 0) / total, 2), total)
                   for name, reg, total, present in rows if total and 100 * (present or 0) / total < 75]
        if not at_risk:
            answer = "No students below 75% attendance were found in the recorded attendance for your department."
        else:
            answer = "Students below 75% attendance in your department:\n" + "\n".join(
                f"- {name} ({reg}): {pct}% ({total} recorded sessions)"
                for name, reg, pct, total in at_risk
            )
        return {"answer": answer, "sources": []}
    finally:
        db.close()


def build_router():
    workflow = StateGraph(AgentState)

    workflow.add_node("router", route_question)
    workflow.add_node("academic", academic_agent)
    workflow.add_node("university", university_agent)
    workflow.add_node(
        "student_success",
        student_success_agent,
    )
    workflow.add_node("faculty_intelligence", faculty_intelligence_agent)

    workflow.add_edge(START, "router")

    workflow.add_conditional_edges(
        "router",
        lambda state: state["route"],
        {
            "academic": "academic",
            "university": "university",
            "student_success": "student_success",
            "faculty_intelligence": "faculty_intelligence",
        },
    )

    workflow.add_edge("academic", END)
    workflow.add_edge("university", END)
    workflow.add_edge("student_success", END)
    workflow.add_edge("faculty_intelligence", END)

    return workflow.compile()


router = build_router()


def run_agent(
    question: str,
    user_id: int | None = None,
    user_role: str = "STUDENT",
):
    state = {
        "question": question,
    }

    if user_id is not None:
        state["user_id"] = user_id
    state["user_role"] = user_role

    return router.invoke(state)


if __name__ == "__main__":
    result = run_agent(
        "What is my attendance percentage?",
        user_id=267,
    )

    print("=" * 70)
    print("ROUTE:", result["route"])
    print("ANSWER:")
    print(result["answer"])
    print("=" * 70)
