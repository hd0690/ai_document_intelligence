"""
Document service: orchestrates the full ingestion pipeline.

Flow:
  1. Save uploaded file to disk
  2. Parse → extract text
  3. Chunk text into overlapping windows
  4. Embed each chunk
  5. Upsert into Chroma

An in-process registry (dict) tracks document metadata for Phase 1.
Phase 2 will replace this with a proper SQLite-backed repository.
"""

import logging
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from app.config import Settings
from app.core.indexing.embedder import embed_texts
from app.core.indexing.vector_store import add_chunks, delete_document, list_document_ids
from app.core.ingestion.chunker import chunk_text
from app.core.ingestion.parser import parse_document
from app.models.document import DocumentRecord, DocumentStatus

logger = logging.getLogger(__name__)

# ── In-process document registry (Phase 1) ───────────────────────────────────
# Keyed by document_id. Replaced by SQLite in Phase 2.
_document_registry: dict[str, DocumentRecord] = {}


def ingest_document(file_path: Path, filename: str, settings: Settings) -> DocumentRecord:
    """
    Run the full ingestion pipeline for an uploaded file.

    Args:
        file_path: Path to the saved upload file.
        filename:  Original filename (used in metadata / citations).
        settings:  Application settings.

    Returns:
        DocumentRecord reflecting the final state (indexed or failed).
    """
    document_id = str(uuid.uuid4())
    record = DocumentRecord(
        document_id=document_id,
        filename=filename,
        file_type=Path(filename).suffix.lower().lstrip("."),
        status=DocumentStatus.PROCESSING,
        created_at=datetime.utcnow(),
    )
    _document_registry[document_id] = record

    try:
        # Step 1 — Parse
        raw_text = parse_document(file_path)

        # Step 2 — Chunk
        chunks = chunk_text(
            text=raw_text,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            metadata={"document_id": document_id, "filename": filename},
        )

        # Step 3 — Embed
        texts = [c.text for c in chunks]
        embeddings = embed_texts(texts, settings.embedding_model)

        # Step 4 — Store
        add_chunks(
            document_id=document_id,
            filename=filename,
            chunk_texts=texts,
            embeddings=embeddings,
            persist_dir=settings.chroma_persist_dir,
            collection_name=settings.chroma_collection_name,
        )

        record.status = DocumentStatus.INDEXED
        record.chunk_count = len(chunks)
        logger.info("Document '%s' indexed with %d chunks (id=%s)", filename, len(chunks), document_id)

    except Exception as exc:
        record.status = DocumentStatus.FAILED
        record.error = str(exc)
        logger.exception("Failed to index document '%s': %s", filename, exc)

    return record


def save_upload(upload_file_bytes: bytes, filename: str, upload_dir: str) -> Path:
    """Persist raw upload bytes to the uploads directory, return the path."""
    dest = Path(upload_dir) / filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(upload_file_bytes)
    return dest


def get_all_documents() -> list[DocumentRecord]:
    """Return all tracked documents (in-process registry, Phase 1)."""
    return list(_document_registry.values())


def get_document(document_id: str) -> DocumentRecord | None:
    return _document_registry.get(document_id)


def remove_document(document_id: str, settings: Settings) -> bool:
    """
    Delete a document from the registry and from Chroma.
    Returns True if the document existed, False otherwise.
    """
    record = _document_registry.pop(document_id, None)
    if record is None:
        return False

    delete_document(
        document_id=document_id,
        persist_dir=settings.chroma_persist_dir,
        collection_name=settings.chroma_collection_name,
    )

    upload_path = Path(settings.upload_dir) / record.filename
    if upload_path.exists():
        upload_path.unlink()

    return True
