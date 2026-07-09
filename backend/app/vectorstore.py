"""
ChromaDB vector store wrapper, embedding with Google's hosted Gemini
embedding API (same GEMINI_API_KEY you already have - no local model,
no torch, tiny memory footprint). This matters on constrained hosting
(e.g. Render's free 512MB instances), where a local sentence-transformers
+ torch stack can exceed available RAM and get silently killed mid-request.
"""
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from app.config import settings

_embeddings = None
_vectorstore = None


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
        )
    return _embeddings


def get_vectorstore() -> Chroma:
    """Returns a singleton Chroma vector store instance, persisted to disk."""
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(
            collection_name=settings.CHROMA_COLLECTION,
            embedding_function=get_embeddings(),
            persist_directory=settings.CHROMA_PERSIST_DIR,
        )
    return _vectorstore


def reset_collection():
    """Used by /admin/reindex to wipe and rebuild the collection from scratch."""
    global _vectorstore
    vs = get_vectorstore()
    try:
        ids = vs.get()["ids"]
        if ids:
            vs.delete(ids=ids)
    except Exception:
        pass
    return vs