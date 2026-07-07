"""
Run once (locally or as a Render "Job") to seed the knowledge base with the
college's official documents before the API goes live, e.g.:

    python seed_documents.py data/Student-Handbook.pdf
    python seed_documents.py data/*.pdf

Put the FULL Student Handbook PDF (and any fee circulars, syllabus PDFs,
hostel rules, etc.) in backend/data/ and list them here or pass as args.
"""
import sys
import os
import shutil
import uuid

sys.path.insert(0, os.path.dirname(__file__))

from app.config import settings
from app import ingestion


def seed(filepaths):
    for path in filepaths:
        if not os.path.exists(path):
            print(f"  SKIP (not found): {path}")
            continue
        filename = os.path.basename(path)
        safe_name = f"{uuid.uuid4().hex}_{filename}"
        dest = os.path.join(settings.DOCS_DIR, safe_name)
        shutil.copy(path, dest)
        result = ingestion.ingest_file(dest, filename)
        print(f"  Indexed '{filename}': {result['chunks_indexed']} chunks (doc_id={result['doc_id']})")


if __name__ == "__main__":
    files = sys.argv[1:]
    if not files:
        default_dir = os.path.join(os.path.dirname(__file__), "data")
        if os.path.isdir(default_dir):
            files = [os.path.join(default_dir, f) for f in os.listdir(default_dir)
                     if f.lower().endswith((".pdf", ".docx", ".txt"))]
    if not files:
        print("No files given and none found in backend/data/. "
              "Usage: python seed_documents.py path/to/handbook.pdf")
        sys.exit(1)

    print(f"Seeding {len(files)} document(s) into ChromaDB at {settings.CHROMA_PERSIST_DIR}...")
    seed(files)
    print("Done.")
