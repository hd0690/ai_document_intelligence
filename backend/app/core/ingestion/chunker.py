"""
Document chunker: splits extracted text into overlapping chunks for indexing.

Why chunking?
  LLMs have context limits and embedding models work best on focused passages.
  Chunking lets us retrieve only the most relevant pieces for a given query.

Strategy (Phase 1): fixed-size sliding window with overlap.
  chunk_size   — max characters per chunk (configurable via settings)
  chunk_overlap — characters shared between adjacent chunks (preserves context
                  across chunk boundaries)

Phase 2 will explore sentence-aware and semantic chunking strategies.
"""

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    text: str
    index: int          # 0-based position in the document
    char_start: int     # character offset in original text
    char_end: int       # character offset in original text
    metadata: dict = field(default_factory=dict)


def chunk_text(
    text: str,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
    metadata: dict | None = None,
) -> list[Chunk]:
    """
    Split *text* into overlapping fixed-size chunks.

    Args:
        text:          Full document text.
        chunk_size:    Max characters per chunk.
        chunk_overlap: Characters of overlap between adjacent chunks.
        metadata:      Arbitrary metadata attached to every chunk (e.g. filename,
                       document_id). Stored in the vector store alongside the
                       embedding so we can surface citations at query time.

    Returns:
        Ordered list of Chunk objects.
    """
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    base_meta = metadata or {}
    chunks: list[Chunk] = []
    step = chunk_size - chunk_overlap
    start = 0
    index = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_text_slice = text[start:end].strip()

        # Skip whitespace-only slices that can occur at end of document
        if chunk_text_slice:
            chunks.append(
                Chunk(
                    text=chunk_text_slice,
                    index=index,
                    char_start=start,
                    char_end=end,
                    metadata={**base_meta, "chunk_index": index},
                )
            )
            index += 1

        start += step

    logger.debug(
        "Chunked document into %d chunks (size=%d, overlap=%d)",
        len(chunks),
        chunk_size,
        chunk_overlap,
    )
    return chunks
