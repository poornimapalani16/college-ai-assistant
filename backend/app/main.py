import os
import shutil
import uuid

from fastapi import FastAPI, UploadFile, File, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import (
    ChatRequest, ChatResponse, SourceChunk,
    UploadResponse, ReindexResponse, DocumentInfo,
)
from app.rag_graph import run_chat
from app import ingestion

app = FastAPI(
    title="College AI Assistant API",
    description="RAG-powered assistant for students, parents, faculty, and staff.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def require_admin(x_admin_key: str = Header(default="")):
    if x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing admin key")
    return True


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/college-info")
def college_info():
    """Frontend reads this to render the landing page branding dynamically."""
    return {
        "name": settings.COLLEGE_NAME,
        "short_name": settings.COLLEGE_SHORT_NAME,
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        result = run_chat(question=req.message, session_id=req.session_id, role=req.role)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat pipeline failed: {e}")

    return ChatResponse(
        answer=result["answer"],
        sources=[SourceChunk(**s) for s in result["sources"]],
        session_id=req.session_id,
    )


# ---------------------------------------------------------------------------
# Admin endpoints: Upload / Delete / Re-index / Manage chatbot knowledge
# All require header  X-Admin-Key: <ADMIN_API_KEY>
# ---------------------------------------------------------------------------

@app.post("/api/admin/documents", response_model=UploadResponse, dependencies=[Depends(require_admin)])
async def upload_document(file: UploadFile = File(...)):
    allowed_ext = (".pdf", ".docx", ".doc", ".txt")
    if not file.filename.lower().endswith(allowed_ext):
        raise HTTPException(400, f"Unsupported file type. Allowed: {allowed_ext}")

    safe_name = f"{uuid.uuid4().hex}_{file.filename}"
    dest_path = os.path.join(settings.DOCS_DIR, safe_name)
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = ingestion.ingest_file(dest_path, file.filename)
    except Exception as e:
        os.remove(dest_path)
        raise HTTPException(500, f"Ingestion failed: {e}")

    return UploadResponse(
        doc_id=result["doc_id"],
        filename=result["filename"],
        chunks_indexed=result["chunks_indexed"],
        message="Document uploaded and indexed successfully.",
    )


@app.get("/api/admin/documents", response_model=list[DocumentInfo], dependencies=[Depends(require_admin)])
def get_documents():
    return [DocumentInfo(**d) for d in ingestion.list_documents()]


@app.delete("/api/admin/documents/{doc_id}", dependencies=[Depends(require_admin)])
def delete_document(doc_id: str):
    success = ingestion.delete_document(doc_id)
    if not success:
        raise HTTPException(404, "Document not found")
    return {"message": "Document deleted and removed from the index."}


@app.post("/api/admin/reindex", response_model=ReindexResponse, dependencies=[Depends(require_admin)])
def reindex():
    result = ingestion.reindex_all()
    return ReindexResponse(
        documents_processed=result["documents_processed"],
        total_chunks=result["total_chunks"],
        message="Full re-index complete.",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
