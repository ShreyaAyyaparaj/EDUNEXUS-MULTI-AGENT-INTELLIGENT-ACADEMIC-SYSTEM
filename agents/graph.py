from typing import Dict, Any
from sqlalchemy.orm import Session

from agents.state import AgentState
from agents.nodes.student_success import run_student_success_node
from agents.nodes.mentor_discovery import run_mentor_discovery_node
from agents.nodes.placement_assistant import run_placement_assistant_node
from agents.nodes.admin_predictions import run_admin_predictions_node

def classify_intent(query: str) -> str:
    q_lower = query.lower()
    
    if any(k in q_lower for k in ["mentor", "guide", "faculty", "research interest", "professor", "advisor"]):
        return "mentor_discovery"
    elif any(k in q_lower for k in ["risk", "attendance drop", "failing", "warning", "my cgpa"]):
        return "student_success"
    elif any(k in q_lower for k in ["predict", "forecast", "future", "placement rate", "trend"]):
        return "admin_prediction"
    else:
        return "placement_rag"

def run_agent_graph(query: str, user: Any, db: Session) -> Dict[str, Any]:
    """
    LangGraph Orchestrator Execution Entry Point.
    Routes queries to Agent 1, 2, 3, or 4 gracefully.
    """
    intent = classify_intent(query)
    
    state: AgentState = {
        "query": query,
        "user_id": user.id if user else 1,
        "user_role": user.role.value if hasattr(user.role, "value") else str(user.role),
        "user_department_id": getattr(user, "department_id", 1),
        "classified_intent": intent,
        "at_risk_data": None,
        "mentor_matches": None,
        "retrieved_chunks": None,
        "prediction_summary": None,
        "final_response": "",
        "grounding_docs": [],
        "agent_used": intent,
        "is_fallback": False
    }

    try:
        if intent == "mentor_discovery":
            res_state = run_mentor_discovery_node(state, db)
        elif intent == "student_success":
            res_state = run_student_success_node(state, db)
        elif intent == "admin_prediction":
            res_state = run_admin_predictions_node(state, db)
        else:
            res_state = run_placement_assistant_node(state)

        return {
            "response": res_state.get("final_response", ""),
            "agent_used": res_state.get("agent_used", intent),
            "grounding_docs": res_state.get("grounding_docs", [])
        }

    except Exception as e:
        # Ultimate LangGraph execution guard
        return {
            "response": f"EduNexus Agent system responded: I can help answer questions regarding placement guidelines, faculty mentors, or academic rules. (Error: {str(e)})",
            "agent_used": "fallback_guard",
            "grounding_docs": []
        }
