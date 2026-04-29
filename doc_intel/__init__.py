"""Document Intelligence Tool - RAG System.

A Python CLI-based tool for building Retrieval-Augmented Generation (RAG) systems
that allows users to upload documents, embed them, and query them using an LLM.
"""

__version__ = "0.1.0"
__author__ = "AI Team"

from config import settings
from ingestion import load_documents, chunk_documents, generate_embeddings
from retrieval import VectorStoreManager, DocumentRetriever
from llm import LLMGenerator
from utils import setup_logger, get_logger, log_query

__all__ = [
    "settings",
    "load_documents",
    "chunk_documents",
    "generate_embeddings",
    "VectorStoreManager",
    "DocumentRetriever",
    "LLMGenerator",
    "setup_logger",
    "get_logger",
    "log_query",
]
