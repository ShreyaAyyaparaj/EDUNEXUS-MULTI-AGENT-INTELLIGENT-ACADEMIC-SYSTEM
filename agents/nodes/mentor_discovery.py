from typing import List, Dict, Any
from sqlalchemy.orm import Session
from agents.llm import call_gemini_llm
from agents.retrievers.vector_store import vector_store
from app.models.all_models import FacultyProfile, User

def run_mentor_discovery_node(state: dict, db: Session) -> dict:
    query = state.get("query", "")

    # Retrieve vector matches from ChromaDB faculty collection
    matches = vector_store.search_faculty_mentors(query, top_k=3)
    
    # Check live availability field in database
    available_faculty_matches = []
    for match in matches:
        meta = match.get("metadata", {})
        fac_id = meta.get("faculty_id")
        
        if fac_id:
            fac = db.query(FacultyProfile).filter(FacultyProfile.id == fac_id).first()
            if fac and fac.is_available_for_mentorship:
                available_faculty_matches.append({
                    "id": fac.id,
                    "name": fac.user.full_name if fac.user else "Faculty Member",
                    "designation": fac.designation,
                    "research_interests": fac.research_interests,
                    "bio": fac.bio
                })
        else:
            # Fallback mock check
            available_faculty_matches.append({
                "id": 1,
                "name": meta.get("name", "Dr. Aris Thorne"),
                "designation": meta.get("designation", "Associate Professor"),
                "research_interests": "Deep Learning, Natural Language Processing",
                "bio": "Leading researcher in AI in Education."
            })

    if not available_faculty_matches:
        # Fallback to default available faculty in DB
        facs = db.query(FacultyProfile).filter(FacultyProfile.is_available_for_mentorship == True).all()
        for f in facs:
            available_faculty_matches.append({
                "id": f.id,
                "name": f.user.full_name if f.user else "Faculty",
                "designation": f.designation,
                "research_interests": f.research_interests,
                "bio": f.bio
            })

    # Gemini synthesis for why this mentor fits
    match_descriptions = "\n".join([
        f"- {m['name']} ({m['designation']}): Research in {m['research_interests']}"
        for m in available_faculty_matches[:2]
    ])

    prompt = f"""
    Student Interest Query: "{query}"

    Available Faculty Matches:
    {match_descriptions}

    Explain in 2-3 bullet points why these faculty members align with the student's request and recommend who they should send a mentorship request to.
    """

    response = call_gemini_llm(
        prompt=prompt,
        system_instruction="You are EduNexus Mentor Discovery Agent. Match students with faculty based on research interests.",
        agent_name="mentor_discovery_agent",
        fallback_response=f"Top Recommended Mentor: {available_faculty_matches[0]['name']} ({available_faculty_matches[0]['designation']}). Research Focus: {available_faculty_matches[0]['research_interests']}."
    )

    return {
        **state,
        "mentor_matches": available_faculty_matches,
        "final_response": response,
        "agent_used": "mentor_discovery"
    }
