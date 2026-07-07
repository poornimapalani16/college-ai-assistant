from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="The user's question")
    session_id: str = Field(..., description="Stable id for this conversation/browser session")
    role: Literal["student", "parent", "faculty", "admin"] = "student"
    history: Optional[List[ChatMessage]] = None  # optional client-supplied history override


class SourceChunk(BaseModel):
    document_name: str
    page: Optional[int] = None
    snippet: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
    session_id: str


class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    chunk_count: int
    uploaded_at: str


class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    chunks_indexed: int
    message: str


class ReindexResponse(BaseModel):
    documents_processed: int
    total_chunks: int
    message: str
