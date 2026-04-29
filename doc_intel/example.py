"""Example script showing programmatic usage of Document Intelligence Tool."""

import sys
from pathlib import Path

# Add parent directory to path to import doc_intel
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from ingestion import load_documents, chunk_documents, generate_embeddings
from retrieval import VectorStoreManager, DocumentRetriever
from llm import LLMGenerator
from utils import log_query, print_query_pipeline


def main():
    """Run example workflow."""
    print("🚀 Document Intelligence Tool - Example Usage\n")

    # Example 1: Ingest documents
    print("=" * 80)
    print("Step 1: Ingesting Documents")
    print("=" * 80)

    docs_dir = settings.docs_dir
    print(f"📁 Loading documents from: {docs_dir}")

    try:
        # Load documents
        documents = load_documents(str(docs_dir))
        print(f"✓ Loaded {len(documents)} documents\n")

        if not documents:
            print("ℹ️  No documents found. Please add documents to:", docs_dir)
            print("Skipping to retrieval demo...\n")
            # Continue to demo retrieval if documents exist
            demo_retrieval()
            return

        # Chunk documents
        chunks = chunk_documents(documents)
        print(f"✓ Created {len(chunks)} chunks")

        # Generate embeddings
        print("🔢 Generating embeddings...")
        nodes = generate_embeddings(chunks)
        print(f"✓ Generated embeddings for {len(nodes)} nodes\n")

        # Store in database
        print("💾 Storing in vector database...")
        vector_store = VectorStoreManager()
        vector_store.add_documents(nodes)
        print("✓ Documents stored successfully\n")

    except Exception as e:
        print(f"❌ Error during ingestion: {e}")
        return

    # Example 2: Query documents
    demo_query()


def demo_query():
    """Demonstrate querying documents."""
    print("=" * 80)
    print("Step 2: Querying Documents")
    print("=" * 80)

    questions = [
        "What is the main topic?",
        "Can you summarize the content?",
        "What are the key points?",
    ]

    for question in questions:
        print(f"\n❓ Question: {question}")

        try:
            # Retrieve documents
            retriever = DocumentRetriever()
            chunks = retriever.retrieve(question, k=3)
            print(f"✓ Retrieved {len(chunks)} relevant chunks")

            # Generate response
            llm = LLMGenerator()
            response = llm.generate(question, chunks)

            print(f"🤖 Answer: {response}\n")

            # Log the query
            prompt = llm.generate_prompt(question, chunks)
            log_query(question, chunks, prompt, response)

        except Exception as e:
            print(f"❌ Error: {e}")


def demo_retrieval():
    """Demonstrate retrieval with existing documents."""
    print("=" * 80)
    print("Step 2: Querying Documents (Retrieval Demo)")
    print("=" * 80)

    try:
        # Check if vector store has documents
        vector_store = VectorStoreManager()
        info = vector_store.get_collection_info()

        print(f"📊 Vector Store Status:")
        print(f"  Collection: {info['name']}")
        print(f"  Documents: {info['count']}\n")

        if info['count'] == 0:
            print("ℹ️  No documents in vector store. Ingest documents first.\n")
            return

        # Demo retrieval
        test_query = "What is this about?"
        print(f"❓ Test Query: {test_query}")

        retriever = DocumentRetriever()
        chunks = retriever.retrieve(test_query, k=3)

        print(f"✓ Retrieved {len(chunks)} chunks\n")

        for i, chunk in enumerate(chunks, 1):
            preview = chunk[:200].replace("\n", " ") + "..."
            print(f"[Chunk {i}] {preview}\n")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
