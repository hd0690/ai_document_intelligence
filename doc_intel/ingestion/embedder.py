"""Embedding generator using Ollama."""

from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.schema import TextNode

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


def get_embedding_model() -> OllamaEmbedding:
    """
    Initialize and return the Ollama embedding model.

    Returns:
        OllamaEmbedding instance
    """
    logger.info(
        f"Initializing Ollama embeddings: "
        f"model={settings.ollama_embedding_model}, "
        f"url={settings.ollama_base_url}"
    )

    embedding_model = OllamaEmbedding(
        model_name=settings.ollama_embedding_model,
        base_url=settings.ollama_base_url,
    )

    return embedding_model


def generate_embeddings(nodes: list[TextNode]) -> list[TextNode]:
    """
    Generate embeddings for a list of TextNode objects.

    Args:
        nodes: List of TextNode objects

    Returns:
        List of TextNode objects with embeddings
    """
    embedding_model = get_embedding_model()

    logger.info(f"Generating embeddings for {len(nodes)} nodes...")

    # Generate embeddings
    for i, node in enumerate(nodes):
        try:
            embedding = embedding_model.get_text_embedding(node.get_content())
            node.embedding = embedding
            if (i + 1) % 10 == 0:
                logger.debug(f"Generated embeddings for {i + 1}/{len(nodes)} nodes")
        except Exception as e:
            logger.error(f"Error generating embedding for node {i}: {e}")
            raise

    logger.info(f"Successfully generated embeddings for {len(nodes)} nodes")
    return nodes
