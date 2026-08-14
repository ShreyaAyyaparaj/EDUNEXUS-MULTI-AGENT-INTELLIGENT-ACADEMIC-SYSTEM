import os
import sys
import shutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.config import settings

def clean_and_seed():
    chroma_dir = settings.CHROMA_PERSIST_DIR
    print(f"Cleaning existing ChromaDB directory at: {chroma_dir}")
    if os.path.exists(chroma_dir):
        shutil.rmtree(chroma_dir, ignore_errors=True)
    os.makedirs(chroma_dir, exist_ok=True)

    print("Re-importing vector store and seeding ChromaDB...")
    from app.db.session import SessionLocal
    from app.models.all_models import FacultyProfile
    from agents.retrievers.vector_store import vector_store

    docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../docs"))
    vector_store.seed_documents(docs_dir)

    db = SessionLocal()
    faculties = db.query(FacultyProfile).all()
    fac_list = []
    for f in faculties:
        fac_list.append({
            "id": f.id,
            "name": f.user.full_name if f.user else "Faculty",
            "designation": f.designation,
            "research_interests": f.research_interests,
            "bio": f.bio,
            "is_available": f.is_available_for_mentorship
        })
    db.close()

    vector_store.seed_faculty_vectors(fac_list)
    print("ChromaDB Vector Store seeding completed successfully!")

if __name__ == "__main__":
    clean_and_seed()
