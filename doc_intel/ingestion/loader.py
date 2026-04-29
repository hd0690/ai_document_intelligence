"""Document loader for the ingestion pipeline."""

from pathlib import Path

from llama_index.core import SimpleDirectoryReader
from llama_index.core.schema import Document

from utils.logger import get_logger

logger = get_logger(__name__)


def load_documents(directory: str) -> list[Document]:
    """
    Load documents from a directory using LlamaIndex SimpleDirectoryReader.

    Supports: .pdf, .txt, .md, .docx, .pptx

    Args:
        directory: Path to directory containing documents

    Returns:
        List of LlamaIndex Document objects
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    if not dir_path.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")

    logger.info(f"Loading documents from: {directory}")

    reader = SimpleDirectoryReader(input_dir=str(dir_path), recursive=True)
    documents = reader.load_data()

    logger.info(f"Successfully loaded {len(documents)} documents")

    for doc in documents:
        logger.debug(f"Loaded: {doc.metadata.get('file_name', 'unknown')}")

    return documents


def load_single_document(file_path: str) -> Document:
    """
    Load a single document from a file path.

    Args:
        file_path: Path to the document file

    Returns:
        LlamaIndex Document object
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    logger.info(f"Loading document from: {file_path}")

    reader = SimpleDirectoryReader(input_files=[str(file_path)])
    documents = reader.load_data()

    if not documents:
        raise ValueError(f"No documents loaded from: {file_path}")

    logger.info(f"Successfully loaded document: {file_path.name}")
    return documents[0]
