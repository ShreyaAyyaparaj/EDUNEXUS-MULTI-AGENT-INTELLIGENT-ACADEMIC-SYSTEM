from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR / "chroma"

COLLECTION_NAME = "edunexus_knowledge"

_model = None
_collection = None


def get_model():
    global _model

    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")

    return _model


def get_collection():
    global _collection

    if _collection is None:
        client = chromadb.PersistentClient(
            path=str(CHROMA_DIR)
        )

        _collection = client.get_collection(
            name=COLLECTION_NAME
        )

    return _collection


def search(query: str, top_k: int = 5):
    model = get_model()
    collection = get_collection()

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True,
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    matches = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        matches.append({
            "content": document,
            "source": metadata.get("source"),
            "page": metadata.get("page"),
            "chunk": metadata.get("chunk"),
            "distance": distance,
        })

    return matches


def main():
    print("=" * 70)
    print("EduNexus RAG RETRIEVER TEST")
    print("=" * 70)

    questions = [
        "What subjects are included in Semester VII?",
        "What is Project Evaluation I?",
        "What is the vision of Rajalakshmi Engineering College?",
        "What policies does Rajalakshmi Engineering College have?",
    ]

    for question in questions:
        print("\n" + "-" * 70)
        print(f"QUERY: {question}")
        print("-" * 70)

        results = search(question, top_k=3)

        for index, result in enumerate(results, start=1):
            print(f"\n[{index}]")
            print(
                f"Source: {result['source']} | "
                f"Page: {result['page']} | "
                f"Distance: {result['distance']:.4f}"
            )
            print(result["content"][:700])


if __name__ == "__main__":
    main()
