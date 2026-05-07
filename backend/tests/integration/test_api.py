"""
Integration test: upload a plain-text file → query it → get an answer.

Runs against the real FastAPI app with mocked LLM (so no Ollama needed).
Chroma uses an in-memory mode by overriding the persist directory.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.dependencies import get_app_settings
from app.main import create_app


@pytest.fixture()
def tmp_settings(tmp_path: Path) -> Settings:
    """Override storage paths to a temp directory so tests don't pollute real storage."""
    return Settings(
        upload_dir=str(tmp_path / "uploads"),
        processed_dir=str(tmp_path / "processed"),
        chroma_persist_dir=str(tmp_path / "chroma"),
        chroma_collection_name="test_collection",
        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
        llm_provider="ollama",
        ollama_model="llama3.2",
    )


@pytest.fixture()
def client(tmp_settings: Settings) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_app_settings] = lambda: tmp_settings
    return TestClient(app)


def test_health(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_upload_txt_and_list(client: TestClient):
    content = b"The speed of light is approximately 299,792,458 metres per second."
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("physics.txt", content, "text/plain")},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "indexed"
    assert data["filename"] == "physics.txt"

    list_resp = client.get("/api/v1/documents")
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] == 1


def test_upload_unsupported_type(client: TestClient):
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("image.png", b"fake-image-bytes", "image/png")},
    )
    assert response.status_code == 415


def test_query_after_upload(client: TestClient):
    content = b"Python is a high-level programming language known for its readability."
    client.post(
        "/api/v1/documents/upload",
        files={"file": ("python.txt", content, "text/plain")},
    )

    # Mock the LLM call so the test doesn't require Ollama to be running
    with patch(
        "app.core.rag.generator._call_ollama",
        return_value="Python is a high-level programming language.",
    ):
        resp = client.post(
            "/api/v1/query",
            json={"question": "What is Python?"},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert "answer" in body
    assert "sources" in body
    assert len(body["sources"]) >= 1
