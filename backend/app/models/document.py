from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: DocumentStatus
    message: str


class DocumentRecord(BaseModel):
    document_id: str
    filename: str
    file_type: str
    status: DocumentStatus
    chunk_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    error: str | None = None


class DocumentListResponse(BaseModel):
    documents: list[DocumentRecord]
    total: int
