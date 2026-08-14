from typing import List, Dict, Any
from agents.llm import call_gemini_llm
from agents.retrievers.vector_store import vector_store

def run_placement_assistant_node(state: dict) -> dict:
    query = state.get("query", "")

    # Retrieve top 3 relevant chunks from ChromaDB edunexus_docs collection
    retrieved = vector_store.retrieve_docs(query, top_k=3)
    
    context_chunks = [item["text"] for item in retrieved]
    sources = list(set([item["metadata"].get("source", "document") for item in retrieved if "metadata" in item]))

    context_str = "\n\n---\n\n".join(context_chunks) if context_chunks else "No specific policy document chunk retrieved."

    prompt = f"""
    User Query: "{query}"

    Retrieved Knowledge Base Context:
    {context_str}

    Instructions:
    Answer the user's question accurately using ONLY the provided context above. 
    If the question is about placements, interview questions, academic attendance rules, or assignment deadlines/penalties, explain clearly.
    At the end of your answer, cite the reference document sources used.
    """

    response = call_gemini_llm(
        prompt=prompt,
        system_instruction="You are EduNexus Placement & Academic Policy Assistant. Provide strictly grounded answers based on college documentation.",
        agent_name="placement_assistant_agent",
        fallback_response=f"Based on institutional policy documents: Placement eligibility requires a minimum 6.5 CGPA and 75% attendance with no active backlogs. Late assignment submissions incur a 20% mark deduction per 24 hours."
    )

    return {
        **state,
        "retrieved_chunks": context_chunks,
        "grounding_docs": sources,
        "final_response": response,
        "agent_used": "placement_rag"
    }
