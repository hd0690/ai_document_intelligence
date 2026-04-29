# Architecture Overview

## System Design

Document Intelligence Tool is a modular RAG (Retrieval-Augmented Generation) system built with Python. The architecture follows a clean, layered approach.

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI INTERFACE (Typer)                     │
├─────────────────────────────────────────────────────────────┤
│  • ingest <dir>     - Load and store documents               │
│  • ask <query>      - Query documents                        │
│  • info             - Database info                          │
│  • clear-db         - Clear database                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
    ┌───▼───┐    ┌───▼────┐   ┌───▼────┐
    │Ingest │    │Retriev │   │   LLM  │
    │       │    │ al     │   │        │
    └───┬───┘    └───┬────┘   └───┬────┘
        │            │            │
    ┌───▼────────────┼────────────▼──┐
    │   Core Processing Modules      │
    ├────────────────────────────────┤
    │ • Document Loading             │
    │ • Chunking (Token-based)       │
    │ • Embedding Generation         │
    │ • Vector Search                │
    │ • Prompt Engineering           │
    │ • Response Generation          │
    └────────────┬───────────────────┘
                 │
        ┌────────┼────────┐
        │        │        │
    ┌───▼──┐ ┌──▼───┐ ┌──▼────┐
    │Chroma│ │Ollama│ │OpenRouter
    │DB    │ │      │ │API
    │      │ │      │ │
    └──────┘ └──────┘ └───────┘
  (Vector  (Embedding (LLM
   Store)   Model)    Model)
```

## Module Breakdown

### 1. **Ingestion Pipeline** (`ingestion/`)

Responsible for loading documents and preparing them for storage.

```
ingestion/
├── loader.py          # Load documents from files/directories
│   └─ Supports: PDF, TXT, MD, DOCX, PPTX
├── chunker.py         # Split documents into manageable chunks
│   └─ Token-based splitting (default: 500 tokens, 50 overlap)
└── embedder.py        # Generate vector embeddings
    └─ Uses Ollama (nomic-embed-text)
```

**Flow:**
```
Files → Load → Chunk → Embed → Store
```

### 2. **Retrieval Pipeline** (`retrieval/`)

Handles vector storage and semantic search.

```
retrieval/
├── vector_store.py    # ChromaDB management
│   ├─ Initialize DB
│   ├─ Add documents
│   └─ Manage collections
└── retriever.py       # Semantic search
    └─ Query → Embed → Search → Retrieve
```

**Flow:**
```
Query → Embed → Vector Search → Retrieved Chunks
```

### 3. **LLM Generation** (`llm/`)

Generates contextual responses using OpenRouter API.

```
llm/
└── generator.py       # OpenRouter LLM interface
    ├─ Prompt engineering
    ├─ API communication
    └─ Response generation (normal & streaming)
```

**Flow:**
```
Query + Chunks → Prompt → OpenRouter API → Response
```

### 4. **Utilities** (`utils/`)

Cross-cutting concerns like logging and debugging.

```
utils/
├── logger.py          # Structured logging to console and files
│   ├─ Query logging (JSON format)
│   └─ Application logging
└── debug.py           # Debug mode utilities
    ├─ Print query pipeline
    ├─ Show retrieved chunks
    └─ Display final prompt
```

### 5. **Configuration** (`config.py`)

Centralized settings management with environment variable support.

```
config.py
├─ API Keys (OpenRouter)
├─ Model Settings (Ollama)
├─ Database Configuration (ChromaDB)
├─ Processing Parameters (chunk size, top-k)
└─ Logging & Debug Settings
```

## Data Flow

### Ingestion Flow

```
Document File
    │
    ├─> Load (SimpleDirectoryReader)
    │      └─> Document object
    │
    ├─> Chunk (TokenSplitter)
    │      └─> TextNode[] with text
    │
    ├─> Embed (Ollama)
    │      └─> TextNode[] with embeddings
    │
    └─> Store (ChromaDB)
           └─> Persistent vector store
```

### Query Flow

```
User Query
    │
    ├─> Embed (Ollama)
    │      └─> Query vector
    │
    ├─> Search (ChromaDB)
    │      └─> Retrieved chunks (top-k)
    │
    ├─> Build Prompt (Template)
    │      └─> Context + Query
    │
    ├─> Generate (OpenRouter)
    │      └─> LLM response
    │
    └─> Log & Display
           └─> JSON log + Console output
```

## Key Components

### 1. **ChromaDB (Vector Store)**
- Persistent storage in `data/chroma_db/`
- Collection-based organization
- Similarity search via embeddings

### 2. **Ollama (Embedding Model)**
- Local embedding generation
- Model: `nomic-embed-text`
- Runs on `http://localhost:11434`

### 3. **OpenRouter API (LLM)**
- Remote LLM inference
- Model: `meta-llama/llama-2-70b-chat` (configurable)
- Supports streaming responses

### 4. **Typer (CLI)**
- Command-line interface
- Rich formatted output
- Built-in help and validation

## Configuration Hierarchy

```
1. .env file (highest priority)
2. Environment variables
3. Default values in config.py
```

Example `.env`:
```env
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=meta-llama/llama-2-70b-chat
OLLAMA_BASE_URL=http://localhost:11434
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RETRIEVAL=5
DEBUG=false
```

## Error Handling

- **Document Loading**: Validates paths and formats
- **Chunking**: Handles various file types gracefully
- **Embedding**: Graceful fallback if Ollama unavailable
- **Retrieval**: Empty results handled cleanly
- **LLM API**: Retry logic and error messages
- **Storage**: Transaction safety with logging

## Performance Considerations

1. **Embedding Generation**: Cached locally, no re-computation
2. **Vector Search**: O(1) approximate nearest neighbor (ANN)
3. **Chunk Size**: Balanced between context and token limit
4. **Batch Processing**: Processes documents in chunks
5. **API Calls**: Streaming support for large responses

## Extensibility Points

1. **Alternative Embeddings**: Swap Ollama with other providers
2. **Alternative Vector Store**: Replace ChromaDB with Pinecone, Weaviate, etc.
3. **Alternative LLM**: Use different OpenRouter models or other providers
4. **Custom Chunking**: Implement domain-specific chunking strategies
5. **Post-processing**: Add custom logic to retrieved results

## Security Considerations

- **API Keys**: Stored in `.env`, never in code
- **Database**: Local storage by default
- **Logs**: JSON format with full context (separate file)
- **Input Validation**: All user inputs validated
- **Error Messages**: Safe error reporting without exposing internals
