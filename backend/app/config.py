"""
Central configuration for the College AI Assistant backend.
All secrets are read from environment variables (.env locally, or the
Render dashboard's "Environment" tab in production). Nothing sensitive
is hard-coded.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings:
    # --- LLM ---
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    # --- Embeddings ---
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # --- Vector store ---
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "chroma_db"))
    CHROMA_COLLECTION: str = os.getenv("CHROMA_COLLECTION", "college_documents")

    # --- Chunking ---
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "150"))
    TOP_K: int = int(os.getenv("TOP_K", "5"))

    # --- Storage for uploaded source documents ---
    DOCS_DIR: str = os.getenv("DOCS_DIR", str(BASE_DIR / "documents"))

    # --- Admin ---
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "change-me")

    # --- College branding (drives the /api/college-info endpoint the frontend reads) ---
    COLLEGE_NAME: str = os.getenv("COLLEGE_NAME", "O.P. Jindal Global University")
    COLLEGE_SHORT_NAME: str = os.getenv("COLLEGE_SHORT_NAME", "JGU")

    # --- CORS ---
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "*").split(",")

settings = Settings()
os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
os.makedirs(settings.DOCS_DIR, exist_ok=True)
