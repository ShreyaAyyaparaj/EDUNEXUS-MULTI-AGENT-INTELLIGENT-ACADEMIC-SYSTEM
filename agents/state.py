from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    query: str
    user_id: int
    user_role: str
    user_department_id: Optional[int]
    classified_intent: str # "student_success", "mentor_discovery", "placement_rag", "admin_prediction", "general"
    at_risk_data: Optional[List[Dict[str, Any]]]
    mentor_matches: Optional[List[Dict[str, Any]]]
    retrieved_chunks: Optional[List[str]]
    prediction_summary: Optional[Dict[str, Any]]
    final_response: str
    grounding_docs: Optional[List[str]]
    agent_used: str
    is_fallback: bool
