"""
Unit tests for the chunker.

These test pure logic — no I/O, no external dependencies.
"""

import pytest

from app.core.ingestion.chunker import Chunk, chunk_text


def test_basic_chunking():
    text = "A" * 1000
    chunks = chunk_text(text, chunk_size=200, chunk_overlap=50)
    assert len(chunks) > 1
    for chunk in chunks:
        assert isinstance(chunk, Chunk)
        assert len(chunk.text) <= 200


def test_chunk_overlap():
    text = "Hello " * 200  # 1200 chars
    chunks = chunk_text(text, chunk_size=100, chunk_overlap=20)
    # Adjacent chunks should share content due to overlap
    for i in range(len(chunks) - 1):
        end_of_current = chunks[i].char_end
        start_of_next = chunks[i + 1].char_start
        assert start_of_next < end_of_current


def test_short_text_single_chunk():
    text = "Short text."
    chunks = chunk_text(text, chunk_size=200, chunk_overlap=20)
    assert len(chunks) == 1
    assert chunks[0].text == text.strip()


def test_chunk_metadata_propagation():
    text = "X" * 500
    meta = {"document_id": "doc-123", "filename": "test.pdf"}
    chunks = chunk_text(text, chunk_size=200, chunk_overlap=0, metadata=meta)
    for chunk in chunks:
        assert chunk.metadata["document_id"] == "doc-123"
        assert chunk.metadata["filename"] == "test.pdf"
        assert "chunk_index" in chunk.metadata


def test_invalid_overlap_raises():
    with pytest.raises(ValueError, match="chunk_overlap must be smaller"):
        chunk_text("abc", chunk_size=100, chunk_overlap=100)


def test_empty_text_returns_no_chunks():
    chunks = chunk_text("", chunk_size=200, chunk_overlap=20)
    assert chunks == []


def test_whitespace_only_text_returns_no_chunks():
    chunks = chunk_text("   \n\n\t  ", chunk_size=200, chunk_overlap=20)
    assert chunks == []
