"""Unit tests for Document Intelligence Tool."""

import pytest
from pathlib import Path

from config import settings
from ingestion.chunker import chunk_text
from ingestion.embedder import get_embedding_model
from utils.logger import get_logger


def test_config_loading():
    """Test that config loads correctly."""
    assert settings.chunk_size == 500
    assert settings.chunk_overlap == 50
    assert settings.top_k_retrieval == 5
    assert settings.chroma_collection_name == "documents"


def test_logger_setup():
    """Test logger initialization."""
    logger = get_logger("test")
    assert logger is not None
    assert logger.name == "test"


def test_chunk_text():
    """Test text chunking."""
    sample_text = """
    This is a sample document for testing.
    It contains multiple sentences and paragraphs.
    The chunker should split this into smaller pieces.
    """ * 50  # Repeat to have enough tokens

    chunks = chunk_text(sample_text)
    assert len(chunks) > 0
    assert all(hasattr(chunk, "get_content") for chunk in chunks)


def test_embedding_model():
    """Test embedding model initialization."""
    try:
        model = get_embedding_model()
        assert model is not None
    except Exception as e:
        pytest.skip(f"Ollama not available: {e}")


def test_config_directories():
    """Test that required directories are created."""
    assert settings.logs_dir.exists()
    assert settings.docs_dir.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
