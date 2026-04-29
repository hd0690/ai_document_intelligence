"""Document chunker for the ingestion pipeline."""

from llama_index.core.schema import BaseNode, TextNode, Document
from llama_index.core.node_parser import SentenceSplitter

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


def chunk_documents(documents: list[Document]) -> list[TextNode]:
    """
    Split documents into chunks using token-based splitting.

    Args:
        documents: List of LlamaIndex Document objects
        settings.chunk_size: Target chunk size in tokens
        settings.chunk_overlap: Number of overlapping tokens between chunks

    Returns:
        List of TextNode objects representing chunks
    """
    logger.info(
        f"Chunking documents: size={settings.chunk_size}, overlap={settings.chunk_overlap}"
    )

    splitter = SentenceSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    nodes: list[BaseNode] = splitter.get_nodes_from_documents(documents)

    # Convert to TextNode for consistency
    text_nodes = [
        node if isinstance(node, TextNode) else TextNode(text=node.get_content())
        for node in nodes
    ]

    logger.info(f"Created {len(text_nodes)} chunks from {len(documents)} documents")

    return text_nodes


def chunk_text(text: str) -> list[TextNode]:
    """
    Chunk raw text into TextNode objects.

    Args:
        text: Raw text to chunk

    Returns:
        List of TextNode objects
    """
    doc = Document(text=text)
    return chunk_documents([doc])
