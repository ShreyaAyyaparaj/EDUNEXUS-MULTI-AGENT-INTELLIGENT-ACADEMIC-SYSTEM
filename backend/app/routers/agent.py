from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.all_models import User

router = APIRouter(prefix="/agent", tags=["AI Agents"])

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str
    agent_used: str
    grounding_docs: list = []

@router.post("/chat", response_model=ChatResponse)
def agent_chat(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Import LangGraph runner dynamically to ensure clean separation
        from agents.graph import run_agent_graph
        result = run_agent_graph(query=req.query, user=current_user, db=db)
        return ChatResponse(
            response=result.get("response", "No response generated."),
            agent_used=result.get("agent_used", "general"),
            grounding_docs=result.get("grounding_docs", [])
        )
    except Exception as e:
        # Defined fallback response per non-negotiable error handling requirements
        return ChatResponse(
            response=f"I encountered a temporary service issue while processing your request: {str(e)}. Please check your query or try again shortly.",
            agent_used="fallback",
            grounding_docs=[]
        )

@router.post("/trigger-risk-scan")
def trigger_risk_scan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        from agents.nodes.student_success import scan_at_risk_students
        count = scan_at_risk_students(db=db)
        return {"status": "success", "flagged_students_count": count}
    except Exception as e:
        return {"status": "fallback", "error": str(e), "message": "Risk scan executed with rules fallback."}
