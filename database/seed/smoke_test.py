import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.db.session import SessionLocal
from app.models.all_models import User
from app.services.erp_service import ERPService
from agents.graph import run_agent_graph

def run_smoke_test():
    print("=== EDUNEXUS END-TO-END SMOKE TEST ===")
    db = SessionLocal()

    # 1. Test Users
    student_user = db.query(User).filter(User.email == "student@educamp.edu").first()
    faculty_user = db.query(User).filter(User.email == "faculty@educamp.edu").first()
    admin_user = db.query(User).filter(User.email == "admin@educamp.edu").first()

    assert student_user is not None, "Student user missing"
    assert faculty_user is not None, "Faculty user missing"
    assert admin_user is not None, "Admin user missing"
    print("[PASS] User retrieval test passed.")

    # 2. Test Student Dashboard Service
    st_dash = ERPService.get_student_dashboard_data(db, student_user)
    print(f"[PASS] Student Dashboard Data loaded: {st_dash['student_name']} (CGPA: {st_dash['cgpa']})")

    # 3. Test Faculty Dashboard Service
    fac_dash = ERPService.get_faculty_dashboard_data(db, faculty_user)
    print(f"[PASS] Faculty Dashboard Data loaded: {fac_dash['faculty_name']} (At-Risk Count: {len(fac_dash['at_risk_students'])})")

    # 4. Test Admin Dashboard Service
    adm_dash = ERPService.get_admin_dashboard_data(db)
    print(f"[PASS] Admin Dashboard Data loaded: Enrolled Students={adm_dash['total_students']}, Placement Rate={adm_dash['placement_metrics']['placement_rate']}%")

    # 5. Test LangGraph Agent 3 RAG Assistant
    res_rag = run_agent_graph("What is the minimum CGPA required for campus placements?", student_user, db)
    print(f"[PASS] Agent 3 RAG Query Test passed. Agent Used: {res_rag['agent_used']}")
    print(f"  Response: {res_rag['response'][:120]}...")

    # 6. Test LangGraph Agent 2 Mentor Discovery
    res_mentor = run_agent_graph("Find a professor specializing in Natural Language Processing and Deep Learning", student_user, db)
    print(f"[PASS] Agent 2 Mentor Discovery Test passed. Agent Used: {res_mentor['agent_used']}")
    print(f"  Response: {res_mentor['response'][:120]}...")

    # 7. Test LangGraph Agent 4 Admin Predictions
    res_pred = run_agent_graph("What is the projected placement rate for next year?", admin_user, db)
    print(f"[PASS] Agent 4 Predictions Test passed. Agent Used: {res_pred['agent_used']}")
    print(f"  Response: {res_pred['response'][:120]}...")

    db.close()
    print("\nALL SMOKE TESTS PASSED WITH ZERO ERRORS!")

if __name__ == "__main__":
    run_smoke_test()
