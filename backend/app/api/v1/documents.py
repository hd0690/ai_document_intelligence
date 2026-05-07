import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.config import Settings
from app.core.ingestion.parser import SUPPORTED_EXTENSIONS
from app.dependencies import get_app_settings
from app.models.document import DocumentListResponse, DocumentRecord, DocumentUploadResponse
from app.services.document_service import (
    get_all_documents,
    get_document,
    ingest_document,
    remove_document,
    save_upload,
)

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)

# 50 MB upload limit
MAX_UPLOAD_BYTES = 50 * 1024 * 1024


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile,
    settings: Settings = Depends(get_app_settings),
) -> DocumentUploadResponse:
    """
    Upload a document and trigger the ingestion pipeline.

    Accepted file types: PDF, TXT, MD.
    """
    ext = Path(file.filename or "").suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type '{ext}' is not supported. Accepted: {sorted(SUPPORTED_EXTENSIONS)}",
        )

    raw_bytes = await file.read()
    if len(raw_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {MAX_UPLOAD_BYTES // (1024*1024)} MB",
        )

    filename = file.filename or "unnamed"
    file_path = save_upload(raw_bytes, filename, settings.upload_dir)
    record = ingest_document(file_path=file_path, filename=filename, settings=settings)

    return DocumentUploadResponse(
        document_id=record.document_id,
        filename=record.filename,
        status=record.status,
        message=(
            f"Document indexed with {record.chunk_count} chunks."
            if record.status.value == "indexed"
            else f"Ingestion failed: {record.error}"
        ),
    )


@router.get("", response_model=DocumentListResponse)
def list_documents() -> DocumentListResponse:
    """Return all uploaded documents and their status."""
    documents = get_all_documents()
    return DocumentListResponse(documents=documents, total=len(documents))


@router.get("/{document_id}", response_model=DocumentRecord)
def get_document_detail(document_id: str) -> DocumentRecord:
    """Get details for a single document by ID."""
    record = get_document(document_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return record


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document_endpoint(
    document_id: str,
    settings: Settings = Depends(get_app_settings),
) -> None:
    """Delete a document and remove all its indexed chunks from the vector store."""
    found = remove_document(document_id, settings)
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
