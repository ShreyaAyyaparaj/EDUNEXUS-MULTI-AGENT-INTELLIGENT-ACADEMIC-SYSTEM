from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models.entities import User
from app.services.agent_service import run_agent


router = APIRouter(
    prefix="/api/copilot",
    tags=["Academic Copilot"],
)


class CopilotRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=2,
        max_length=2000,
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
    )


class CopilotSource(BaseModel):
    source: str
    page: int | None = None


class CopilotResponse(BaseModel):
    route: str
    answer: str
    sources: list[CopilotSource]


@router.post(
    "/ask",
    response_model=CopilotResponse,
)
def ask_copilot(
    request: CopilotRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = run_agent(
            question=request.question,
            user_id=current_user.id,
            user_role=current_user.role,
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {str(exc)}",
        )
