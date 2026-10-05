from pathlib import Path
import hashlib
import re

import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "documents"
CHROMA_DIR = BASE_DIR / "chroma"

COLLECTION_NAME = "edunexus_knowledge"

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str):
    text = clean_text(text)

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - CHUNK_OVERLAP

    return chunks


def load_documents():
    documents = []
    metadatas = []
    ids = []

    pdf_files = sorted(DOCUMENTS_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in {DOCUMENTS_DIR}"
        )

    print(f"Found {len(pdf_files)} PDF files.")

    for pdf_path in pdf_files:
        print(f"\nReading: {pdf_path.name}")

        reader = PdfReader(str(pdf_path))

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            chunks = chunk_text(text)

            for chunk_index, chunk in enumerate(chunks):
                raw_id = (
                    f"{pdf_path.name}|"
                    f"{page_number}|"
                    f"{chunk_index}|"
                    f"{chunk}"
                )

                chunk_id = hashlib.sha256(
                    raw_id.encode("utf-8")
                ).hexdigest()

                documents.append(chunk)

                metadatas.append({
                    "source": pdf_path.name,
                    "page": page_number,
                    "chunk": chunk_index,
                })

                ids.append(chunk_id)

    return documents, metadatas, ids


def main():
    print("=" * 70)
    print("EduNexus RAG INGESTION")
    print("=" * 70)

    print("\nLoading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Embedding model loaded.")

    documents, metadatas, ids = load_documents()

    print(f"\nTotal chunks: {len(documents)}")

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    try:
        client.delete_collection(COLLECTION_NAME)
        print("Existing collection deleted.")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    batch_size = 64

    for start in range(0, len(documents), batch_size):
        end = min(start + batch_size, len(documents))

        batch_documents = documents[start:end]
        batch_metadatas = metadatas[start:end]
        batch_ids = ids[start:end]

        print(
            f"Embedding chunks {start + 1}-{end} "
            f"of {len(documents)}..."
        )

        embeddings = model.encode(
            batch_documents,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).tolist()

        collection.add(
            ids=batch_ids,
            documents=batch_documents,
            metadatas=batch_metadatas,
            embeddings=embeddings,
        )

    print("\n" + "=" * 70)
    print("INGESTION COMPLETE")
    print("=" * 70)
    print(f"Collection : {COLLECTION_NAME}")
    print(f"Documents  : {len(documents)}")
    print(f"Database   : {CHROMA_DIR}")


if __name__ == "__main__":
    main()
