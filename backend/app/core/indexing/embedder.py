"""
Embedder: thin wrapper around a HuggingFace sentence-transformers model.

Why local embeddings?
  - No API cost or latency
  - Reproducible (same model = same vectors)
  - Easy to swap: change EMBEDDING_MODEL in .env and re-index

The embedder is intentionally stateless — just a function that converts text
to a float vector. The vector store handles persistence.
"""

import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _load_model(model_name: str):
    """Load and cache the embedding model (expensive, do once per process)."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as e:
        raise RuntimeError(
            "sentence-transformers is not installed. "
            "Run: uv add sentence-transformers"
        ) from e

    logger.info("Loading embedding model: %s", model_name)
    return SentenceTransformer(model_name)


def embed_texts(texts: list[str], model_name: str) -> list[list[float]]:
    """
    Generate embeddings for a list of texts.

    Args:
        texts:      List of strings to embed.
        model_name: HuggingFace model identifier (e.g. 'sentence-transformers/all-MiniLM-L6-v2').

    Returns:
        List of float vectors, one per input text.
    """
    if not texts:
        return []

    model = _load_model(model_name)
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return embeddings.tolist()


def embed_query(query: str, model_name: str) -> list[float]:
    """Convenience wrapper for embedding a single query string."""
    return embed_texts([query], model_name)[0]
