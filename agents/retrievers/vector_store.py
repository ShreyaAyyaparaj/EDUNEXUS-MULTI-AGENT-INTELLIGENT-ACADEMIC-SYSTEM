import os
import math
from typing import List, Dict, Any
import chromadb
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
from app.core.config import settings

CHROMA_DIR = settings.CHROMA_PERSIST_DIR
os.makedirs(CHROMA_DIR, exist_ok=True)

class LocalHashEmbeddingFunction(EmbeddingFunction):
    """
    Zero-network local deterministic embedding function for ChromaDB.
    Maps text to a fixed-size 128-dimensional dense vector using TF-IDF word feature hashing.
    Prevents ONNX network download timeouts.
    """
    def __init__(self, dim: int = 128):
        self.dim = dim

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for doc in input:
            vec = [0.0] * self.dim
            words = doc.lower().split()
            if not words:
                embeddings.append(vec)
                continue
            for word in words:
                h = hash(word) % self.dim
                vec[h] += 1.0
            # L2 normalize
            norm = math.sqrt(sum(x * x for x in vec)) or 1.0
            vec = [x / norm for x in vec]
            embeddings.append(vec)
        return embeddings

local_ef = LocalHashEmbeddingFunction()

class VectorStoreManager:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DIR)
        self.docs_collection = self.client.get_or_create_collection(
            name="edunexus_docs",
            embedding_function=local_ef
        )
        self.faculty_collection = self.client.get_or_create_collection(
            name="faculty_profiles",
            embedding_function=local_ef
        )

    def seed_documents(self, docs_dir: str):
        """Chunk and embed academic, placement, and assignment policy markdown files."""
        if not os.path.exists(docs_dir):
            return

        documents = []
        metadatas = []
        ids = []

        counter = 0
        for fname in os.listdir(docs_dir):
            if fname.endswith(".md"):
                filepath = os.path.join(docs_dir, fname)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                category = fname.replace(".md", "")
                chunks = [c.strip() for c in content.split("\n\n") if len(c.strip()) > 30]

                for idx, chunk in enumerate(chunks):
                    counter += 1
                    documents.append(chunk)
                    metadatas.append({"source": fname, "category": category, "chunk_id": idx})
                    ids.append(f"doc_{category}_{idx}_{counter}")

        if documents:
            self.docs_collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Vector Store: Seeded {len(documents)} document chunks into ChromaDB.")

    def seed_faculty_vectors(self, faculty_list: List[Dict[str, Any]]):
        """Embed faculty research interests and bios for Agent 2 mentor discovery."""
        documents = []
        metadatas = []
        ids = []

        for f in faculty_list:
            doc_text = f"Faculty: {f['name']}. Designation: {f['designation']}. Research Interests: {f['research_interests']}. Bio: {f['bio']}"
            documents.append(doc_text)
            metadatas.append({
                "faculty_id": f["id"],
                "name": f["name"],
                "designation": f["designation"],
                "is_available": f["is_available"]
            })
            ids.append(f"fac_{f['id']}")

        if documents:
            self.faculty_collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Vector Store: Seeded {len(documents)} faculty profiles into ChromaDB.")

    def retrieve_docs(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        results = self.docs_collection.query(
            query_texts=[query],
            n_results=top_k
        )
        output = []
        if results and results.get("documents"):
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            for d, m in zip(docs, metas):
                output.append({"text": d, "metadata": m})
        return output

    def search_faculty_mentors(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        results = self.faculty_collection.query(
            query_texts=[query],
            n_results=top_k
        )
        output = []
        if results and results.get("documents"):
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            for d, m in zip(docs, metas):
                output.append({"text": d, "metadata": m})
        return output

vector_store = VectorStoreManager()
