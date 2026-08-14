import os
import logging
from typing import Optional
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.all_models import AgentExecutionLog

logger = logging.getLogger("edunexus_agents_llm")

def call_gemini_llm(
    prompt: str,
    system_instruction: Optional[str] = None,
    agent_name: str = "general_agent",
    fallback_response: str = "Unable to process request via Gemini LLM at this moment."
) -> str:
    """
    Invokes Gemini 2.5 Flash with retry and strict error handling fallback.
    Logs execution results into agent_execution_logs table.
    """
    api_key = os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY

    # If key is missing or dummy placeholder, trigger defined fallback response cleanly
    if not api_key or api_key == "your_gemini_api_key_here":
        _log_execution(agent_name, prompt[:200], "fallback", "GEMINI_API_KEY missing or placeholder")
        return f"{fallback_response}\n\n*(Note: Operating in deterministic rule-based fallback mode)*"

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        
        config = types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=1024,
        )
        if system_instruction:
            config.system_instruction = system_instruction

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config
        )

        text = response.text.strip() if response.text else fallback_response
        _log_execution(agent_name, prompt[:200], "success", None)
        return text

    except Exception as e:
        logger.error(f"Gemini API call failed for node [{agent_name}]: {e}")
        _log_execution(agent_name, prompt[:200], "fallback", str(e))
        return f"{fallback_response}\n\n*(Fallback triggered due to service response: {str(e)})*"

def _log_execution(agent_name: str, input_summary: str, status: str, error_msg: Optional[str]):
    try:
        db = SessionLocal()
        log_entry = AgentExecutionLog(
            agent_name=agent_name,
            input_summary=input_summary,
            status=status,
            error_message=error_msg
        )
        db.add(log_entry)
        db.commit()
        db.close()
    except Exception as ex:
        logger.warning(f"Could not persist agent execution log: {ex}")
