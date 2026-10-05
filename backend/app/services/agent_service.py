import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from agents.router import router


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

    result = router.invoke(state)

    return {
        "route": result.get("route"),
        "answer": result.get("answer", ""),
        "sources": result.get("sources", []),
    }
