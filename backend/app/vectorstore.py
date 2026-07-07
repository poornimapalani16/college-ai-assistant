"""
ChromaDB vector store wrapper, embedding with Sentence-Transformers via
LangChain's HuggingFaceEmbeddings wrapper (runs locally, no API cost).
"""
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from app.config import settings

_embeddings = None
_vectorstore = None


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
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
