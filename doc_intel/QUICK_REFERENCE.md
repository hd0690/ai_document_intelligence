# Quick Reference - Document Intelligence Tool

## 🚀 Quick Start (2 minutes)

```bash
# 1. Setup (one time)
python3.12 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .
cp .env.example .env
# Edit .env and add OPENROUTER_API_KEY

# 2. Start Ollama in another terminal
ollama serve

# 3. Prepare documents
mkdir -p data/docs
cp your_documents/* data/docs/

# 4. Use it!
docintel ingest ./data/docs
docintel ask "Your question?"
```

## 📋 Main Commands

```bash
# Ingest documents
docintel ingest <directory>           # Load documents
docintel ingest <directory> -v        # Verbose output

# Query documents
docintel ask "question"               # Ask question
docintel ask "question" --debug       # Show pipeline
docintel ask "question" --stream      # Stream response

# Database
docintel info                         # Database info
docintel clear-db                     # Clear all docs

# Development
python setup_check.py                 # Check setup
python example.py                     # Run examples
pytest tests.py                       # Run tests
```

## 🎯 Key Files

| What You Need | Where It Is |
|---------------|-----------|
| Main CLI | `cli.py` |
| Configuration | `.env` + `config.py` |
| Document ingestion | `ingestion/` |
| Search & retrieval | `retrieval/` |
| LLM integration | `llm/generator.py` |
| Logging | `utils/logger.py` |
| API reference | `API.md` |
| System design | `ARCHITECTURE.md` |
| Setup guide | `GETTING_STARTED.md` |

## ⚙️ Configuration

Edit `.env`:

```env
# Required: Your API key
OPENROUTER_API_KEY=your_key_here

# Optional: Change defaults
CHUNK_SIZE=500              # Chunk size in tokens
TOP_K_RETRIEVAL=5          # Number of results
DEBUG=false                 # Debug mode
```

## 🔍 Debug Mode

```bash
# See what's happening
docintel ask "question" --debug

# Shows:
# 1. User query
# 2. Retrieved chunks from DB
# 3. Final prompt to LLM
```

## 📊 Workflow

```
Documents → Load → Chunk → Embed → Store in DB
                                      ↓
Query → Embed → Search DB → Retrieve → Generate → Answer
```

## 🔧 Common Tasks

```bash
# Add documents (just copy files)
cp *.pdf data/docs/
docintel ingest ./data/docs

# View logs
tail -f logs/queries.log

# Clear database and start fresh
docintel clear-db
docintel ingest ./data/docs

# Use programmatically
python
>>> from retrieval import DocumentRetriever
>>> retriever = DocumentRetriever()
>>> results = retriever.retrieve("your query")
```

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Connection refused" | Start Ollama: `ollama serve` |
| "No documents found" | Check directory exists: `ls data/docs/` |
| "API key error" | Add to .env: `OPENROUTER_API_KEY=your_key` |
| "Module not found" | Reinstall: `pip install -e .` |

## 📦 Dependencies

### Required
- Python 3.12+
- Ollama (running locally)
- OpenRouter API key

### Python packages
```
typer, llama-index-core, chromadb, pydantic, python-dotenv, httpx
```

## 🧪 Verify Setup

```bash
# All-in-one check
python setup_check.py

# Manual checks
python --version              # Check Python 3.12+
curl http://localhost:11434   # Check Ollama
grep OPENROUTER .env          # Check API key
```

## 📈 Performance

| Operation | Time |
|-----------|------|
| Chunk 100 documents | ~10 seconds |
| Search database | <100ms |
| Generate response | 5-30 seconds |
| Full pipeline | 30-60 seconds |

## 📚 Documentation Map

```
README.md                 ← Start here
├── GETTING_STARTED.md    ← Step-by-step setup
├── API.md                ← Function reference
├── ARCHITECTURE.md       ← System design
├── PROJECT_SUMMARY.md    ← Full overview
└── QUICK_REFERENCE.md    ← This file
```

## 🎓 Code Examples

### Basic Usage
```python
from ingestion import load_documents, chunk_documents, generate_embeddings
from retrieval import VectorStoreManager, DocumentRetriever
from llm import LLMGenerator

# 1. Ingest
docs = load_documents("./documents")
chunks = chunk_documents(docs)
nodes = generate_embeddings(chunks)
store = VectorStoreManager()
store.add_documents(nodes)

# 2. Query
retriever = DocumentRetriever()
chunks = retriever.retrieve("your question")

# 3. Generate
llm = LLMGenerator()
answer = llm.generate("your question", chunks)
print(answer)
```

## 💡 Tips

1. Use `--debug` to understand what's happening
2. Start with one document to test
3. Check logs in `logs/queries.log`
4. Adjust `CHUNK_SIZE` for your documents
5. Use `--stream` for interactive responses

## 🔗 Useful Links

- [LlamaIndex](https://docs.llamaindex.ai/)
- [ChromaDB](https://docs.trychroma.com/)
- [Ollama Models](https://ollama.ai/library)
- [OpenRouter](https://openrouter.ai/models)

## ⏱️ Typical Workflow

```bash
# Monday morning
source .venv/bin/activate
ollama serve &              # Background
docintel ingest ./docs
docintel ask "what's new?"  # Daily briefing

# Adding documents
cp new_docs/* data/docs/
docintel ingest ./data/docs # Re-ingest

# Debug issues
docintel ask "?" --debug    # See what went wrong
tail -f logs/queries.log    # Check logs

# Clean up
docintel clear-db           # Reset if needed
```

## ✅ Checklist Before Using

- [ ] Python 3.12+ installed
- [ ] Ollama running (`ollama serve`)
- [ ] `.env` configured with API key
- [ ] Virtual environment activated
- [ ] Documents in `data/docs/`
- [ ] Successful ingest (`docintel ingest ./data/docs`)
- [ ] Test query works (`docintel ask "test"`)

---

**Need help?** See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed instructions.

**Ready to go!** Run: `docintel ask "your question?"`
