"""
Document ingestion pipeline.

Flow: raw file (PDF / DOCX / TXT) --> LangChain loader --> text chunks
(RecursiveCharacterTextSplitter) --> embed with Sentence-Transformers -->
upsert into ChromaDB with metadata (doc_id, filename, page number).

This is what powers "Admin: Upload documents / Re-index documents" from
the PRD, and also the one-time seeding of the college's official PDFs
(handbook, fee circulars, syllabus PDFs, etc).
"""
import os
import uuid
import json
from datetime import datetime, timezone
from typing import List

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.config import settings
from app.vectorstore import get_vectorstore

REGISTRY_PATH = os.path.join(settings.DOCS_DIR, "_registry.json")


def _load_registry() -> dict:
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "r") as f:
            return json.load(f)
    return {}


def _save_registry(registry: dict):
    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)


def _get_loader(filepath: str):
    ext = filepath.lower().rsplit(".", 1)[-1]
    if ext == "pdf":
        return PyPDFLoader(filepath)
    if ext in ("docx", "doc"):
        return Docx2txtLoader(filepath)
    if ext == "txt":
        return TextLoader(filepath, encoding="utf-8")
    raise ValueError(f"Unsupported file type: .{ext}. Supported: pdf, docx, txt")


def ingest_file(filepath: str, original_filename: str) -> dict:
    """
    Ingests a single file already saved to disk at `filepath`.
    Returns {doc_id, filename, chunks_indexed}.
    """
    loader = _get_loader(filepath)
    raw_docs = loader.load()  # one Document per page (PDF) or whole file (txt/docx)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(raw_docs)

    doc_id = str(uuid.uuid4())
    for i, chunk in enumerate(chunks):
        chunk.metadata["doc_id"] = doc_id
        chunk.metadata["filename"] = original_filename
        chunk.metadata["chunk_index"] = i
        # PyPDFLoader already sets metadata["page"]; default to None otherwise
        if chunk.metadata.get("page") is None:
         chunk.metadata["page"] = -1
    vectorstore = get_vectorstore()
    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    vectorstore.add_documents(chunks, ids=ids)

    registry = _load_registry()
    registry[doc_id] = {
        "filename": original_filename,
        "chunk_count": len(chunks),
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "stored_path": filepath,
    }
    _save_registry(registry)

    return {"doc_id": doc_id, "filename": original_filename, "chunks_indexed": len(chunks)}


def list_documents() -> List[dict]:
    registry = _load_registry()
    return [
        {"doc_id": k, "filename": v["filename"], "chunk_count": v["chunk_count"], "uploaded_at": v["uploaded_at"]}
        for k, v in registry.items()
    ]


def delete_document(doc_id: str) -> bool:
    registry = _load_registry()
    if doc_id not in registry:
        return False

    vectorstore = get_vectorstore()
    # delete every chunk belonging to this doc_id
    existing = vectorstore.get(where={"doc_id": doc_id})
    if existing and existing.get("ids"):
        vectorstore.delete(ids=existing["ids"])

    stored_path = registry[doc_id].get("stored_path")
    if stored_path and os.path.exists(stored_path):
        os.remove(stored_path)

    del registry[doc_id]
    _save_registry(registry)
    return True


def reindex_all() -> dict:
    """Wipes the vector store and re-ingests every file currently in DOCS_DIR."""
    from app.vectorstore import reset_collection
    reset_collection()

    registry = _load_registry()
    total_chunks = 0
    processed = 0
    new_registry = {}

    for doc_id, meta in registry.items():
        stored_path = meta.get("stored_path")
        if not stored_path or not os.path.exists(stored_path):
            continue
        result = ingest_file(stored_path, meta["filename"])
        new_registry[result["doc_id"]] = {
            "filename": result["filename"],
            "chunk_count": result["chunks_indexed"],
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "stored_path": stored_path,
        }
        total_chunks += result["chunks_indexed"]
        processed += 1

    _save_registry(new_registry)
    return {"documents_processed": processed, "total_chunks": total_chunks}
