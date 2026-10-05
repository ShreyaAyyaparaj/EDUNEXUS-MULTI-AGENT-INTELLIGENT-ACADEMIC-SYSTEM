from typing import List, Dict, Any
from sqlalchemy.orm import Session
from agents.llm import call_gemini_llm
from app.models.all_models import StudentProfile, Attendance, Mark, AssignmentSubmission, Notification, User

def scan_at_risk_students(db: Session) -> int:
    """
    Agent 1 execution function.
    Deterministic rule-based pre-filter -> Gemini risk summary -> DB Notification write.
    """
    students = db.query(StudentProfile).all()
    flagged_count = 0

    for st in students:
        attendances = db.query(Attendance).filter(Attendance.student_id == st.id).all()
        tot_att = len(attendances)
        pres_att = sum(1 for a in attendances if a.status == "present")
        att_pct = (pres_att / tot_att * 100) if tot_att > 0 else 85.0

        marks = db.query(Mark).filter(Mark.student_id == st.id).all()
        avg_marks = sum(m.score for m in marks) / len(marks) if marks else 75.0

        subs = db.query(AssignmentSubmission).filter(AssignmentSubmission.student_id == st.id).all()
        unsubmitted = sum(1 for s in subs if s.status == "pending")

        # Deterministic Rules Pre-Filter
        if att_pct < 75.0 or avg_marks < 60.0 or unsubmitted >= 2:
            flagged_count += 1
            
            prompt = f"""
            Student: {st.user.full_name} (Roll: {st.roll_number})
            Attendance Rate: {att_pct:.1f}% (Threshold: 75%)
            Average Internal Exam Mark: {avg_marks:.1f}%
            Unsubmitted Assignments: {unsubmitted}

            Provide a 2-sentence empathetic risk summary for the student and a 1-bullet intervention recommendation for their faculty advisor.
            """

            sys_inst = "You are the EduNexus Student Success AI Agent. Provide concise, constructive academic risk evaluations."
            
            risk_summary = call_gemini_llm(
                prompt=prompt,
                system_instruction=sys_inst,
                agent_name="student_success_agent",
                fallback_response=f"Academic Alert: Attendance is {att_pct:.1f}% and average mark is {avg_marks:.1f}%. Please schedule an academic advising session."
            )

            # Write Notification to Student
            n_student = Notification(
                user_id=st.user_id,
                title="Academic Risk Warning & Support",
                message=risk_summary,
                type="risk_alert",
                is_read=False
            )
            db.add(n_student)

            # Write Notification to Advisor if assigned
            if st.advisor_id:
                n_advisor = Notification(
                    user_id=st.advisor_id,
                    title=f"At-Risk Alert: {st.user.full_name}",
                    message=f"Student {st.user.full_name} ({st.roll_number}) has been flagged.\n{risk_summary}",
                    type="risk_alert",
                    is_read=False
                )
                db.add(n_advisor)

    db.commit()
    return flagged_count

def run_student_success_node(state: dict, db: Session) -> dict:
    query = state.get("query", "")
    st_user_id = state.get("user_id")

    student = db.query(StudentProfile).filter(StudentProfile.user_id == st_user_id).first()
    if not student:
        return {
            **state,
            "final_response": "Student profile record not found.",
            "agent_used": "student_success"
        }

    attendances = db.query(Attendance).filter(Attendance.student_id == student.id).all()
    tot_att = len(attendances)
    pres_att = sum(1 for a in attendances if a.status == "present")
    att_pct = (pres_att / tot_att * 100) if tot_att > 0 else 85.0

    prompt = f"Student {student.user.full_name} asks: '{query}'. Their attendance is {att_pct:.1f}% and CGPA is {student.cgpa}."
    
    response = call_gemini_llm(
        prompt=prompt,
        system_instruction="You are EduNexus Student Success Agent. Assist the student with academic guidance.",
        agent_name="student_success_node",
        fallback_response=f"Your current attendance is {att_pct:.1f}% and CGPA is {student.cgpa}. Maintain attendance above 75% for exam eligibility."
    )

    return {
        **state,
        "final_response": response,
        "agent_used": "student_success"
    }
