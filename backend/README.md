# Document Intelligence — Backend

AI-powered document ingestion, semantic search, and question-answering API built with **FastAPI**, **LlamaIndex**, **Chroma**, and local/cloud LLMs.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Quick Start](#quick-start)
4. [Configuration](#configuration)
5. [API Reference](#api-reference)
6. [Core Pipeline](#core-pipeline)
7. [Data Models](#data-models)
8. [Testing](#testing)
9. [Development Guide](#development-guide)
10. [Roadmap](#roadmap)

---

## Architecture Overview

```
                        ┌─────────────────────────────────┐
                        │          FastAPI (HTTP)          │
                        │  /api/v1/documents  /api/v1/query│
                        └────────────┬────────────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                       │
   ┌──────────▼──────────┐  ┌───────▼────────┐  ┌──────────▼──────────┐
   │  Document Service   │  │  Query Service  │  │  (Insights Service) │
   │  parse→chunk→embed  │  │  RAG pipeline   │  │  Phase 3            │
   └──────────┬──────────┘  └───────┬─────────┘  └─────────────────────┘
              │                     │
   ┌──────────▼──────────┐  ┌───────▼─────────────────────────────────┐
   │   Core / Ingestion  │  │            Core / RAG                   │
   │  parser → chunker   │  │  retriever → generator → pipeline       │
   └──────────┬──────────┘  └───────┬─────────────────────────────────┘
              │                     │
   ┌──────────▼──────────────────────▼──────────────────────────────────┐
   │                        Core / Indexing                             │
   │              embedder (HuggingFace)  ·  vector_store (Chroma)     │
   └────────────────────────────────────────────────────────────────────┘
              │                     │
       ┌──────▼──────┐       ┌──────▼──────┐
       │  Local FS   │       │   Chroma DB │
       │  uploads/   │       │  (vectors)  │
       │  processed/ │       └─────────────┘
       └─────────────┘
```

**Request flows:**

| Flow | Steps |
|---|---|
| **Ingest** | Upload file → Parse text → Chunk → Embed → Store in Chroma |
| **Query** | Receive question → Embed question → Similarity search Chroma → LLM generation → Return answer + citations |

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                        # FastAPI app factory, middleware, router registration
│   ├── config.py                      # pydantic-settings; loads .env; validates all config
│   ├── dependencies.py                # FastAPI DI: get_app_settings()
│   │
│   ├── api/v1/
│   │   ├── documents.py               # Upload, list, get, delete document endpoints
│   │   ├── query.py                   # Question-answering endpoint
│   │   └── insights.py               # Placeholder — summarization (Phase 3)
│   │
│   ├── core/
│   │   ├── ingestion/
│   │   │   ├── parser.py              # PDF / TXT / MD → raw text (PyMuPDF)
│   │   │   └── chunker.py             # Sliding-window text chunker with overlap
│   │   ├── indexing/
│   │   │   ├── embedder.py            # HuggingFace sentence-transformers wrapper
│   │   │   └── vector_store.py        # Chroma: add / search / delete / list
│   │   └── rag/
│   │       ├── retriever.py           # Embed query → similarity search
│   │       ├── generator.py           # Prompt assembly + Ollama / OpenRouter call
│   │       └── pipeline.py            # Orchestrates retrieve → generate
│   │
│   ├── models/
│   │   ├── document.py                # DocumentRecord, DocumentStatus, response schemas
│   │   └── query.py                   # QueryRequest, QueryResponse, SourceChunk
│   │
│   └── services/
│       ├── document_service.py        # Ingest pipeline orchestration + in-process registry
│       └── query_service.py           # Delegates to RAG pipeline
│
├── storage/
│   ├── uploads/                       # Raw uploaded files (persisted on disk)
│   ├── processed/                     # Extracted text cache (reserved for Phase 2)
│   └── chroma_db/                     # Chroma persistent vector store
│
├── tests/
│   ├── unit/
│   │   └── test_chunker.py            # 7 unit tests for chunking logic
│   └── integration/
│       └── test_api.py                # Upload + query roundtrip integration tests
│
├── .env                               # Local environment variables (not committed)
├── .env.example                       # Template — copy to .env to get started
└── pyproject.toml                     # Dependencies + build config (managed with uv)
```

---

## Quick Start

### Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | ≥ 3.11 | [python.org](https://python.org) |
| uv | latest | `brew install uv` |
| Ollama | latest | [ollama.ai](https://ollama.ai) (for local LLM) |

### 1. Clone and enter the backend directory

```bash
cd backend
```

### 2. Create the virtual environment and install dependencies

```bash
uv venv --python 3.11
uv sync
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env if you want to change the model, provider, or paths
```

### 4. Start a local LLM (Ollama)

```bash
ollama pull llama3.2
ollama serve          # runs on http://localhost:11434
```

> Skip this if using OpenRouter — set `LLM_PROVIDER=openrouter` and `OPENROUTER_API_KEY` in `.env` instead.

### 5. Start the API server

```bash
uv run uvicorn app.main:app --reload
```

The server starts at **http://localhost:8000**.

| URL | Description |
|---|---|
| http://localhost:8000/docs | Swagger UI (interactive) |
| http://localhost:8000/redoc | ReDoc (readable reference) |
| http://localhost:8000/health | Health check |

---

## Configuration

All settings are loaded from `.env` via `pydantic-settings`. Every key has a sensible default — only `OPENROUTER_API_KEY` is required when using the OpenRouter provider.

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | `development` or `production` |
| `LOG_LEVEL` | `INFO` | Python logging level |
| **LLM** | | |
| `LLM_PROVIDER` | `ollama` | `ollama` or `openrouter` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2` | Model name as listed in `ollama list` |
| `OPENROUTER_API_KEY` | _(empty)_ | Required when `LLM_PROVIDER=openrouter` |
| `OPENROUTER_MODEL` | `openai/gpt-4o-mini` | Any model available on OpenRouter |
| **Embeddings** | | |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | HuggingFace model (runs locally) |
| **Chroma** | | |
| `CHROMA_PERSIST_DIR` | `./storage/chroma_db` | Path for Chroma to persist vectors |
| `CHROMA_COLLECTION_NAME` | `documents` | Chroma collection name |
| **Storage** | | |
| `UPLOAD_DIR` | `./storage/uploads` | Where uploaded files are saved |
| `PROCESSED_DIR` | `./storage/processed` | Reserved for extracted text cache |
| **RAG** | | |
| `RAG_TOP_K` | `5` | Number of chunks retrieved per query |
| `CHUNK_SIZE` | `512` | Max characters per chunk |
| `CHUNK_OVERLAP` | `64` | Overlap characters between adjacent chunks |

> **Important:** `EMBEDDING_MODEL` must stay consistent between ingestion and querying. Changing it after documents are indexed requires re-indexing all documents.

---

## API Reference

Base path: `/api/v1`

### Documents

#### `POST /api/v1/documents/upload`

Upload a document and trigger the ingestion pipeline synchronously.

- **Accepted types:** `.pdf`, `.txt`, `.md`
- **Max size:** 50 MB
- **Content-Type:** `multipart/form-data`

**Request**
```
file: <binary>
```

**Response `201`**
```json
{
  "document_id": "3f2a1b4c-...",
  "filename": "report.pdf",
  "status": "indexed",
  "message": "Document indexed with 42 chunks."
}
```

**Error responses**

| Status | Condition |
|---|---|
| `415` | Unsupported file extension |
| `413` | File exceeds 50 MB |

---

#### `GET /api/v1/documents`

List all uploaded documents.

**Response `200`**
```json
{
  "documents": [
    {
      "document_id": "3f2a1b4c-...",
      "filename": "report.pdf",
      "file_type": "pdf",
      "status": "indexed",
      "chunk_count": 42,
      "created_at": "2026-05-06T10:00:00",
      "error": null
    }
  ],
  "total": 1
}
```

---

#### `GET /api/v1/documents/{document_id}`

Get details for a single document.

**Response `200`** — `DocumentRecord` (see above)
**Response `404`** — document not found

---

#### `DELETE /api/v1/documents/{document_id}`

Delete a document from the registry and remove all its chunks from Chroma.

**Response `204`** — no content
**Response `404`** — document not found

---

### Query

#### `POST /api/v1/query`

Ask a natural-language question over indexed documents.

**Request**
```json
{
  "question": "What are the main findings of the report?",
  "document_ids": ["3f2a1b4c-..."],   // optional — omit to search all documents
  "top_k": 5                           // optional — default 5, max 20
}
```

**Response `200`**
```json
{
  "question": "What are the main findings of the report?",
  "answer": "The main findings indicate...",
  "sources": [
    {
      "document_id": "3f2a1b4c-...",
      "filename": "report.pdf",
      "chunk_text": "The analysis shows that...",
      "score": 0.18
    }
  ]
}
```

> `score` is the cosine distance from Chroma — **lower values = higher similarity** (0.0 is a perfect match).

---

### Health

#### `GET /health`

```json
{ "status": "ok", "env": "development", "llm_provider": "ollama" }
```

---

## Core Pipeline

### Ingestion Pipeline

```
parse_document()  →  chunk_text()  →  embed_texts()  →  add_chunks()
   parser.py           chunker.py      embedder.py     vector_store.py
```

1. **Parse** (`core/ingestion/parser.py`): Reads the file from disk and returns a plain text string.
   - PDF: uses PyMuPDF's `get_text("text")` per page
   - TXT/MD: reads directly with UTF-8 encoding

2. **Chunk** (`core/ingestion/chunker.py`): Splits the text into overlapping windows.
   - Strategy: sliding window — advances by `chunk_size - chunk_overlap` characters per step
   - Each `Chunk` carries character offsets and propagated metadata (document_id, filename)

3. **Embed** (`core/indexing/embedder.py`): Encodes all chunk texts in one batch.
   - Uses `sentence-transformers` via HuggingFace — runs entirely locally
   - Model is loaded once per process and cached via `@lru_cache`

4. **Store** (`core/indexing/vector_store.py`): Upserts chunks into Chroma.
   - Chroma ID format: `{document_id}_chunk_{index}` — makes re-indexing idempotent
   - Cosine similarity space (`hnsw:space: cosine`)

### Query Pipeline (RAG)

```
embed_query()  →  similarity_search()  →  generate_answer()
  embedder.py      vector_store.py         generator.py
```

1. **Retrieve** (`core/rag/retriever.py`): Embeds the question and runs a top-k similarity search against Chroma.

2. **Generate** (`core/rag/generator.py`): Formats a RAG prompt from retrieved chunks and calls the LLM.
   - Prompt instructs the model to answer only from context and say "I don't have enough information" otherwise — reduces hallucination.
   - Provider is selected at runtime from `LLM_PROVIDER` in settings.

3. **Respond** (`core/rag/pipeline.py`): Assembles the `QueryResponse` with the answer and source chunk citations.

---

## Data Models

### `DocumentStatus` (enum)

| Value | Meaning |
|---|---|
| `pending` | Registered but not yet processed |
| `processing` | Ingestion in progress |
| `indexed` | Successfully chunked, embedded, and stored |
| `failed` | Ingestion failed (see `error` field) |

### `DocumentRecord`

| Field | Type | Description |
|---|---|---|
| `document_id` | `str` (UUID) | Unique identifier |
| `filename` | `str` | Original filename |
| `file_type` | `str` | Extension without dot (`pdf`, `txt`, `md`) |
| `status` | `DocumentStatus` | Current ingestion status |
| `chunk_count` | `int` | Number of chunks indexed |
| `created_at` | `datetime` | Upload timestamp |
| `error` | `str \| null` | Error message if `status == failed` |

### `QueryRequest`

| Field | Type | Constraint | Description |
|---|---|---|---|
| `question` | `str` | 1–2000 chars | The user's question |
| `document_ids` | `list[str] \| null` | — | Restrict search scope |
| `top_k` | `int` | 1–20, default 5 | Chunks to retrieve |

### `SourceChunk`

| Field | Type | Description |
|---|---|---|
| `document_id` | `str` | Source document |
| `filename` | `str` | Source filename |
| `chunk_text` | `str` | The actual text passage used |
| `score` | `float` | Cosine distance (lower = more relevant) |

---

## Testing

```bash
# All tests
uv run pytest tests/ -v

# Unit tests only (no external dependencies)
uv run pytest tests/unit/ -v

# Integration tests (requires embedding model; LLM is mocked)
uv run pytest tests/integration/ -v
```

### Test coverage

| File | Type | What it tests |
|---|---|---|
| `tests/unit/test_chunker.py` | Unit | Chunking logic, overlap, metadata propagation, edge cases |
| `tests/integration/test_api.py` | Integration | Health check, upload, list, unsupported type rejection, query roundtrip |

The integration tests use:
- A `tmp_path` fixture for isolated storage (no pollution of real `storage/`)
- `unittest.mock.patch` to mock the LLM call so Ollama is not required to run tests

---

## Development Guide

### Run with auto-reload

```bash
uv run uvicorn app.main:app --reload --port 8000
```

### Lint and format

```bash
uv run ruff check .
uv run ruff format .
```

### Add a new dependency

```bash
uv add <package>          # runtime
uv add --dev <package>    # dev-only
```

### Re-index a document

Delete it via the API, then re-upload. Chroma upserts are idempotent, so uploading the same filename twice is safe as long as `document_id` is consistent (currently each upload generates a new UUID — delete first to avoid duplicates).

### Switch LLM provider

Edit `.env`:
```bash
# Use local Ollama (default)
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2

# Use OpenRouter (cloud)
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=openai/gpt-4o-mini
```
No code changes needed — the generator selects the provider at runtime.

### Switch embedding model

Edit `.env`:
```bash
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5   # higher quality, slower
```

> After changing the embedding model, all existing documents must be re-indexed because old and new embeddings are not compatible.

---

## Roadmap

| Phase | Status | Scope |
|---|---|---|
| **Phase 1 — MVP** | ✅ Complete | Upload, parse, chunk, embed, Chroma, RAG query API |
| **Phase 2 — Robustness** | Planned | OCR (pytesseract), SQLite metadata store, background ingestion (FastAPI BackgroundTasks), structured logging (structlog), broader test coverage |
| **Phase 3 — AI Features** | Planned | Summarization endpoint, key insights extraction, entity recognition |
| **Phase 4 — Production** | Planned | Celery + Redis job queue, Docker + docker-compose, rate limiting, response caching, CI pipeline |
| **Phase 5 — Frontend** | Planned | Minimal React or HTML UI for upload and query |
