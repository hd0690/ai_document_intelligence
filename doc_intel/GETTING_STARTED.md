# Getting Started - Document Intelligence Tool

## 🎯 Goal

By the end of this guide, you'll have a fully functional RAG system that:
- Ingests documents from your computer
- Stores them in a vector database
- Answers questions about them using AI

**Estimated Time:** 15-20 minutes

## 📋 Prerequisites

### Check Your System

```bash
# Python version
python --version  # Must be 3.12+

# All prerequisites
python setup_check.py  # Shows what's missing
```

### What You Need

1. **Python 3.12+** - [Download](https://www.python.org/downloads/)
2. **Ollama** - [Download](https://ollama.ai)
3. **OpenRouter API Key** - [Get Free](https://openrouter.ai)

## 🚀 Step-by-Step Setup

### Step 1: Clone/Navigate to Project

```bash
cd /path/to/doc_intel
```

### Step 2: Create Virtual Environment

```bash
# Create
python3.12 -m venv .venv

# Activate
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows
```

### Step 3: Install Dependencies

```bash
# Option A: Quick install
pip install -e .

# Option B: With dev tools
pip install -e ".[dev]"

# Option C: Using requirements files
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env in your editor
nano .env  # macOS/Linux
# OR
code .env  # VS Code
```

Add your OpenRouter API key:
```env
OPENROUTER_API_KEY=your-api-key-here
```

### Step 5: Start Ollama

```bash
# In a new terminal (keep it running)
ollama serve

# In another terminal, verify it works
curl http://localhost:11434/api/tags
```

### Step 6: Prepare Your Documents

```bash
# Create documents directory
mkdir -p data/docs

# Copy your files or create a sample
cat > data/docs/example.txt << 'EOF'
Python is a high-level, interpreted programming language known for its simplicity and readability.
It was created by Guido van Rossum and first released in 1991.
Python supports multiple programming paradigms including procedural, functional, and object-oriented.
EOF
```

## ✨ Using the Tool

### Basic Workflow

```bash
# 1. Check everything is ready
docintel info

# 2. Ingest documents
docintel ingest ./data/docs

# 3. Ask a question
docintel ask "What is Python?"

# 4. Get an answer!
```

### Example Session

```bash
$ docintel ingest ./data/docs
📂 Loading documents from: ./data/docs
✓ Loaded 1 documents
📄 Chunking documents...
✓ Created 2 chunks
🔢 Generating embeddings...
✓ Generated embeddings for 2 nodes
💾 Storing in vector database...
✓ Successfully stored documents in vector database

Collection: documents
Total Documents: 2
Database Path: ./data/chroma_db

✅ Ingestion complete!

$ docintel ask "What is Python?"
❓ Query: What is Python?
🔍 Retrieving relevant documents...
✓ Retrieved 2 relevant chunks
🤖 Generating response...

Answer:
Python is a high-level, interpreted programming language known for its simplicity
and readability. It was created by Guido van Rossum and first released in 1991.
The language supports multiple programming paradigms including procedural,
functional, and object-oriented approaches, making it versatile for various
applications.

✅ Query complete!
```

## 🐛 Debug Mode

See exactly what's happening inside:

```bash
docintel ask "What is Python?" --debug
```

This shows:
1. The exact query sent
2. Which chunks were retrieved from the database
3. The complete prompt sent to the LLM

## 📊 Streaming Responses

For long responses, stream them token-by-token:

```bash
docintel ask "Explain Python in detail" --stream
```

## 🔍 Database Management

```bash
# View database info
docintel info

# Clear all documents
docintel clear-db

# View query logs
tail -f logs/queries.log

# Pretty-print logs
cat logs/queries.log | python -m json.tool
```

## 📚 Query Examples

Try these queries with your documents:

```bash
# Summaries
docintel ask "Give me a summary of the main points"

# Details
docintel ask "What are the specific details about [topic]?"

# Comparisons
docintel ask "Compare X and Y"

# Definitions
docintel ask "What does X mean?"

# Lists
docintel ask "List all the key features"

# Analysis
docintel ask "What are the implications of [topic]?"
```

## 🛠️ Common Tasks

### Add More Documents

```bash
# Just copy files to data/docs/
cp /path/to/document.pdf data/docs/

# Then re-ingest
docintel ingest ./data/docs
```

### Change Settings

Edit `.env`:

```env
# Use fewer results (faster, less context)
TOP_K_RETRIEVAL=3

# Larger chunks (more context, fewer embeddings)
CHUNK_SIZE=1000

# Different LLM model
OPENROUTER_MODEL=openai/gpt-3.5-turbo
```

### Use Different Embedding Model

```env
OLLAMA_EMBEDDING_MODEL=all-minilm
```

Available models in Ollama:
- `nomic-embed-text` (default, good balance)
- `all-minilm` (smaller, faster)
- `all-mpnet-base-v2` (larger, slower)

## 🧪 Verify Installation

```bash
# All-in-one check
python setup_check.py

# Or manually test each component:

# Test Python
python --version

# Test Ollama
curl http://localhost:11434/api/tags

# Test imports
python -c "import typer; import llama_index; import chromadb; print('✓ All imports OK')"

# Test configuration
python -c "from config import settings; print(settings)"
```

## 📝 Example Workflow for Your First Document

Let's ingest a Wikipedia-like article:

```bash
# 1. Create a sample document
cat > data/docs/machine_learning.txt << 'EOF'
Machine learning is a subset of artificial intelligence (AI) that provides systems 
the ability to automatically learn and improve from experience without being explicitly 
programmed. Machine learning focuses on the development of computer programs that can 
access data and use it to learn for themselves.

The process of learning begins with observations or data, such as examples, direct 
experience, or instruction, in order to look for patterns in data and make better 
decisions in the future based on the examples that we provide. The primary aim is to 
allow the computers to learn automatically without human intervention or assistance 
and adjust actions accordingly.

Types of Machine Learning:
1. Supervised Learning
2. Unsupervised Learning
3. Reinforcement Learning
EOF

# 2. Ingest
docintel ingest ./data/docs -v

# 3. Test queries
docintel ask "What is machine learning?" --debug
docintel ask "What are the types of machine learning?"
docintel ask "How does machine learning work?"

# 4. Check logs
cat logs/queries.log | python -m json.tool
```

## 🆘 Troubleshooting

### "Connection refused" for Ollama
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it in another terminal
ollama serve
```

### "No documents found"
```bash
# Check directory contents
ls -la data/docs/

# Check vector store
docintel info

# Re-ingest
docintel clear-db
docintel ingest ./data/docs -v
```

### "OpenRouter API key error"
```bash
# Verify key in .env
cat .env | grep OPENROUTER_API_KEY

# Verify key is valid (test with curl)
curl https://openrouter.ai/api/v1/models -H "Authorization: Bearer YOUR_KEY"
```

### "Module not found" errors
```bash
# Reinstall in development mode
pip install -e .

# Or using requirements
pip install -r requirements.txt
```

## 📖 Next Steps

1. **Add Your Documents** - Copy your PDFs, docs to `data/docs/`
2. **Customize Settings** - Edit `.env` for your use case
3. **Read ARCHITECTURE.md** - Understand how everything works
4. **Read API.md** - Use the tool programmatically
5. **Check examples/** - See code examples

## 🎓 Learning Resources

- **API Reference:** `API.md` - Detailed API documentation
- **Architecture:** `ARCHITECTURE.md` - System design and data flows
- **Examples:** `example.py` - Programmatic usage examples
- **Tests:** `tests.py` - Unit tests and testing patterns

## 🔗 Useful Links

- [LlamaIndex Docs](https://docs.llamaindex.ai/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Ollama Models](https://ollama.ai/library)
- [OpenRouter Models](https://openrouter.ai/models)

## ✅ Checklist

- [ ] Python 3.12+ installed
- [ ] Ollama installed and running
- [ ] OpenRouter API key obtained
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -e .`)
- [ ] `.env` configured with API key
- [ ] Sample documents in `data/docs/`
- [ ] Documents ingested (`docintel ingest ./data/docs`)
- [ ] Test query works (`docintel ask "test question"`)
- [ ] Debug mode works (`docintel ask "test question" --debug`)

Once all items are checked, you're ready to go! 🚀

## 💡 Tips

1. **Start small** - Use one document first to verify everything works
2. **Debug mode is your friend** - Use `--debug` to understand what's happening
3. **Check logs** - Query logs are in `logs/queries.log` (JSON format)
4. **Experiment with chunks** - Adjust `CHUNK_SIZE` and `TOP_K_RETRIEVAL`
5. **Stream long responses** - Use `--stream` for faster UI feedback
6. **Profile performance** - Log file shows timing information

---

**Ready to get started?** Run:
```bash
python setup_check.py
```

Questions? Check the [README.md](README.md) for more details!
