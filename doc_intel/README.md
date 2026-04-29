# Document Intelligence Tool 🤖

A production-quality Python CLI-based Retrieval-Augmented Generation (RAG) system that allows you to:

- 📄 Upload and ingest documents (PDF, TXT, MD, DOCX, etc.)
- 🧩 Automatically chunk documents with configurable overlap
- 🔢 Generate embeddings using Ollama
- 💾 Store embeddings in persistent ChromaDB
- ❓ Ask natural language questions about your documents
- 🤖 Get contextual answers powered by OpenRouter LLM
- 🐛 Debug mode to inspect the entire RAG pipeline
- 📊 JSON logging of all queries and retrieved context

## 📋 Prerequisites

### System Requirements
- **Python 3.12+**
- **Ollama** (for embeddings) - [Install from ollama.com](https://ollama.com)
- **OpenRouter API Key** - [Get from openrouter.ai](https://openrouter.ai)

### Ollama Setup
```bash
# Install Ollama, then pull the embedding model
ollama pull nomic-embed-text

# Start Ollama (default runs on http://localhost:11434)
ollama serve
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Navigate to the project directory
cd doc_intel

# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 2. Configure Environment Variables

```bash
# Copy the example config
cp .env.example .env

# Edit .env and add your OpenRouter API key
# OPENROUTER_API_KEY=your_actual_api_key_here
```

### 3. Prepare Your Documents

```bash
# Create a documents directory
mkdir -p data/docs

# Add your PDF or text files
cp /path/to/your/documents/* data/docs/
```

### 4. Ingest Documents

```bash
# Ingest all documents from the directory
docintel ingest ./data/docs

# Or with verbose output
docintel ingest ./data/docs -v
```

### 5. Ask Questions

```bash
# Simple query
docintel ask "What is the main topic of the documents?"

# With debug mode (shows retrieved chunks and prompt)
docintel ask "What is the main topic?" --debug

# With streaming response
docintel ask "What is the main topic?" --stream
```

## 📖 CLI Commands

### `docintel ingest <directory>`
Ingest documents from a directory and store them in the vector database.

**Options:**
- `-v, --verbose`: Enable verbose output

**Example:**
```bash
docintel ingest ./documents -v
```

### `docintel ask <query>`
Ask a question and get an answer from the documents.

**Options:**
- `-d, --debug`: Enable debug mode (shows internal pipeline)
- `-s, --stream`: Stream the response token-by-token

**Examples:**
```bash
docintel ask "What are the key features?"
docintel ask "What are the key features?" --debug
docintel ask "What are the key features?" --stream
```

### `docintel info`
Display vector database information.

```bash
docintel info
```

### `docintel clear-db`
Clear all documents from the vector database.

```bash
docintel clear-db
```

## 🔍 Debug Mode

Use the `--debug` flag to inspect the entire RAG pipeline:

```bash
docintel ask "Your question?" --debug
```

This will display:
1. **User Query** - The exact query processed
2. **Retrieved Chunks** - The document chunks retrieved from the vector store
3. **Final Prompt** - The complete prompt sent to the LLM

## 📊 Logging

All queries are logged to `logs/queries.log` in JSON format:

```json
{
  "timestamp": "2024-04-29T12:34:56.789123",
  "query": "What is the main topic?",
  "retrieved_chunks": ["chunk1...", "chunk2..."],
  "final_prompt": "Full prompt sent to LLM",
  "response": "LLM's response"
}
```

View logs:
```bash
tail -f logs/queries.log | python -m json.tool
```

## ⚙️ Configuration

Edit `.env` to customize:

```env
# LLM Settings
OPENROUTER_MODEL=meta-llama/llama-2-70b-chat

# Ollama Settings
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Document Processing
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RETRIEVAL=5

# Debug
DEBUG=false
```

## 📁 Project Structure

```
doc_intel/
├── cli.py                  # Main CLI application
├── config.py              # Configuration management
├── ingestion/
│   ├── loader.py          # Document loading
│   ├── chunker.py         # Document chunking
│   └── embedder.py        # Embedding generation
├── retrieval/
│   ├── vector_store.py    # ChromaDB management
│   └── retriever.py       # Document retrieval
├── llm/
│   └── generator.py       # OpenRouter LLM interface
├── utils/
│   ├── logger.py          # Logging utilities
│   └── debug.py           # Debug utilities
├── data/
│   ├── docs/              # Document storage
│   └── chroma_db/         # Vector database
├── logs/
│   └── queries.log        # Query logs
└── pyproject.toml         # Project dependencies
```

## 🔧 Troubleshooting

### Issue: "Connection refused" for Ollama
**Solution:** Make sure Ollama is running:
```bash
ollama serve
```

### Issue: "OpenRouter API key not provided"
**Solution:** Set your API key in `.env`:
```
OPENROUTER_API_KEY=your_actual_key
```

### Issue: No documents found
**Solution:** Ensure documents are in the correct directory and have supported formats (.pdf, .txt, .md, etc.)

### Issue: "No documents in database"
**Solution:** Ingest documents first:
```bash
docintel ingest ./data/docs
```

## 🧪 Development

### Run Tests
```bash
# Run all tests
pytest

# With coverage
pytest --cov=doc_intel
```

### Code Quality
```bash
# Format code
black .

# Lint
ruff check .

# Type checking
mypy .
```

## 📝 Example Usage

### Step 1: Prepare Documents
```bash
# Create a sample document
cat > data/docs/sample.txt << EOF
Python is a high-level programming language known for its simplicity and readability.
It supports multiple programming paradigms including procedural, functional, and object-oriented.
Python has a large standard library and active community.
EOF
```

### Step 2: Ingest
```bash
docintel ingest ./data/docs
# Output:
# 📂 Loading documents from: ./data/docs
# ✓ Loaded 1 documents
# 📄 Chunking documents...
# ✓ Created 2 chunks
# 🔢 Generating embeddings...
# ✓ Generated embeddings for 2 nodes
# 💾 Storing in vector database...
# ✓ Successfully stored documents in vector database
```

### Step 3: Query
```bash
docintel ask "What is Python?"
# Output:
# ❓ Query: What is Python?
# 🔍 Retrieving relevant documents...
# ✓ Retrieved 2 relevant chunks
# 🤖 Generating response...
# 
# Answer:
# Python is a high-level programming language known for its simplicity and readability.
# It supports multiple programming paradigms including procedural, functional, and
# object-oriented approaches. The language has a large standard library and benefits
# from an active developer community.
```

## 📦 Dependencies

- **typer** - CLI framework
- **llama-index-core** - Document processing and RAG pipeline
- **chroma-db** - Vector database
- **ollama** - Embedding model
- **openai** - OpenRouter API compatibility
- **httpx** - HTTP client
- **pydantic** - Data validation
- **rich** - Terminal formatting

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📧 Support

For issues and questions, please open a GitHub issue.
