"""API Reference - Document Intelligence Tool."""

# This file is for IDE reference. The actual API is defined in the modules.

# ============================================================================
# INGESTION MODULE
# ============================================================================

"""
Module: ingestion/loader.py

Functions:
    load_documents(directory: str) -> list[Document]
        Load documents from a directory using LlamaIndex SimpleDirectoryReader.
        Supported formats: .pdf, .txt, .md, .docx, .pptx
        
        Args:
            directory: Path to directory containing documents
            
        Returns:
            List of LlamaIndex Document objects
            
        Example:
            >>> from ingestion import load_documents
            >>> docs = load_documents("./documents")

    load_single_document(file_path: str) -> Document
        Load a single document from a file path.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            LlamaIndex Document object
"""

# Module: ingestion/chunker.py

"""
Functions:
    chunk_documents(documents: list[Document]) -> list[TextNode]
        Split documents into chunks using token-based splitting.
        Uses settings.chunk_size and settings.chunk_overlap.
        
        Args:
            documents: List of LlamaIndex Document objects
            
        Returns:
            List of TextNode objects representing chunks
            
        Example:
            >>> from ingestion import chunk_documents, load_documents
            >>> docs = load_documents("./documents")
            >>> chunks = chunk_documents(docs)

    chunk_text(text: str) -> list[TextNode]
        Chunk raw text into TextNode objects.
        
        Args:
            text: Raw text to chunk
            
        Returns:
            List of TextNode objects
"""

# Module: ingestion/embedder.py

"""
Functions:
    get_embedding_model() -> OllamaEmbedding
        Initialize and return the Ollama embedding model.
        
        Returns:
            OllamaEmbedding instance
            
        Example:
            >>> from ingestion import get_embedding_model
            >>> model = get_embedding_model()

    generate_embeddings(nodes: list[TextNode]) -> list[TextNode]
        Generate embeddings for a list of TextNode objects.
        Requires Ollama to be running.
        
        Args:
            nodes: List of TextNode objects
            
        Returns:
            List of TextNode objects with embeddings set
            
        Example:
            >>> from ingestion import generate_embeddings
            >>> nodes_with_embeddings = generate_embeddings(chunks)
"""

# ============================================================================
# RETRIEVAL MODULE
# ============================================================================

# Module: retrieval/vector_store.py

"""
Class: VectorStoreManager
    Manages ChromaDB vector store operations.
    
    Methods:
        __init__() -> None
            Initialize ChromaDB client and vector store.
            
        add_documents(nodes: list[TextNode]) -> None
            Add documents/chunks to the vector store.
            
            Args:
                nodes: List of TextNode objects with embeddings
                
            Example:
                >>> from retrieval import VectorStoreManager
                >>> store = VectorStoreManager()
                >>> store.add_documents(nodes_with_embeddings)
        
        get_collection_info() -> dict
            Get information about the current collection.
            
            Returns:
                Dictionary with collection info (name, count, db_path)
                
        clear_collection() -> None
            Clear all documents from the collection.
"""

# Module: retrieval/retriever.py

"""
Class: DocumentRetriever
    Retrieves relevant documents from the vector store.
    
    Methods:
        __init__() -> None
            Initialize the document retriever.
            
        retrieve(query: str, k: int | None = None) -> list[str]
            Retrieve top-k most relevant documents for a query.
            
            Args:
                query: User's query string
                k: Number of documents to retrieve (default: settings.top_k_retrieval)
                
            Returns:
                List of retrieved document chunks
                
            Example:
                >>> from retrieval import DocumentRetriever
                >>> retriever = DocumentRetriever()
                >>> chunks = retriever.retrieve("What is Python?")
        
        retrieve_with_scores(query: str, k: int | None = None) -> list[tuple[str, float]]
            Retrieve top-k documents with similarity scores.
            
            Args:
                query: User's query string
                k: Number of documents to retrieve
                
            Returns:
                List of tuples (document_text, similarity_score)
"""

# ============================================================================
# LLM MODULE
# ============================================================================

# Module: llm/generator.py

"""
Class: LLMGenerator
    Generates responses using OpenRouter API.
    
    Methods:
        __init__(api_key: str | None = None, model: str | None = None) -> None
            Initialize the LLM generator.
            
            Args:
                api_key: OpenRouter API key (default: settings.openrouter_api_key)
                model: Model name (default: settings.openrouter_model)
                
            Example:
                >>> from llm import LLMGenerator
                >>> llm = LLMGenerator()
        
        generate_prompt(query: str, retrieved_chunks: list[str]) -> str
            Build the final prompt for the LLM.
            
            Args:
                query: User's query
                retrieved_chunks: List of retrieved document chunks
                
            Returns:
                Formatted prompt string
        
        generate(query: str, retrieved_chunks: list[str]) -> str
            Generate a response using the OpenRouter API.
            
            Args:
                query: User's query
                retrieved_chunks: List of retrieved document chunks
                
            Returns:
                Generated response from the LLM
                
            Example:
                >>> llm = LLMGenerator()
                >>> response = llm.generate(query, chunks)
        
        stream_generate(query: str, retrieved_chunks: list[str])
            Generate a response using streaming.
            
            Yields:
                Chunks of generated text
                
            Example:
                >>> for chunk in llm.stream_generate(query, chunks):
                >>>     print(chunk, end="")
"""

# ============================================================================
# UTILS MODULE
# ============================================================================

# Module: utils/logger.py

"""
Functions:
    setup_logger(name: str, level: str = "INFO") -> logging.Logger
        Set up a logger with console and file handlers.
        
        Args:
            name: Logger name
            level: Logging level (default: "INFO")
            
        Returns:
            Configured logger instance
    
    log_query(query: str, retrieved_chunks: list[str], final_prompt: str,
              response: str | None = None) -> None
        Log a query to the JSON log file.
        
        Args:
            query: User's query
            retrieved_chunks: List of retrieved document chunks
            final_prompt: Final prompt sent to LLM
            response: LLM's response (optional)
    
    get_logger(name: str) -> logging.Logger
        Get or create a logger instance.
"""

# Module: utils/debug.py

"""
Functions:
    print_debug(title: str, content: Any, separator: bool = True) -> None
        Print debug information if debug mode is enabled.
        
        Args:
            title: Debug section title
            content: Content to print
            separator: Whether to print separator lines
    
    print_retrieved_chunks(chunks: list[str]) -> None
        Print retrieved chunks in debug mode.
        
    print_query_pipeline(query: str, chunks: list[str], prompt: str) -> None
        Print the entire query pipeline in debug mode.
"""

# ============================================================================
# CONFIGURATION
# ============================================================================

# Module: config.py

"""
Class: Settings
    Application settings loaded from environment variables.
    
    Attributes:
        openrouter_api_key: str
        openrouter_model: str
        ollama_base_url: str
        ollama_embedding_model: str
        chroma_db_path: str
        chroma_collection_name: str
        debug: bool
        log_level: str
        log_file: str
        chunk_size: int
        chunk_overlap: int
        top_k_retrieval: int
        data_dir: Path
        docs_dir: Path
        logs_dir: Path
        
    Usage:
        >>> from config import settings
        >>> print(settings.chunk_size)
        500
"""

# ============================================================================
# COMPLETE EXAMPLE
# ============================================================================

"""
Example: Complete RAG Pipeline

    from config import settings
    from ingestion import load_documents, chunk_documents, generate_embeddings
    from retrieval import VectorStoreManager, DocumentRetriever
    from llm import LLMGenerator
    from utils import log_query

    # 1. Ingest Documents
    documents = load_documents("./documents")
    chunks = chunk_documents(documents)
    nodes = generate_embeddings(chunks)
    
    # 2. Store in Vector Database
    store = VectorStoreManager()
    store.add_documents(nodes)
    
    # 3. Query Documents
    query = "What is the main topic?"
    
    # 4. Retrieve Relevant Chunks
    retriever = DocumentRetriever()
    retrieved_chunks = retriever.retrieve(query, k=5)
    
    # 5. Generate Response
    llm = LLMGenerator()
    response = llm.generate(query, retrieved_chunks)
    
    # 6. Log the Query
    prompt = llm.generate_prompt(query, retrieved_chunks)
    log_query(query, retrieved_chunks, prompt, response)
    
    print(response)
"""
