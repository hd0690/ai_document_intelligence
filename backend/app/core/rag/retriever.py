"""
Retriever: takes a user query, embeds it, and returns the most relevant chunks.

This is intentionally a thin layer — it delegates to the embedder and vector
store so each piece stays independently testable.
"""

import logging

from app.core.indexing.embedder import embed_query
from app.core.indexing.vector_store import SearchResult, similarity_search

logger = logging.getLogger(__name__)


def retrieve(
    question: str,
    embedding_model: str,
    chroma_persist_dir: str,
    chroma_collection_name: str,
    top_k: int = 5,
    document_ids: list[str] | None = None,
) -> list[SearchResult]:
    """
    Embed *question* and return the top-k most similar stored chunks.

    Args:
        question:               The user's natural-language query.
        embedding_model:        HuggingFace model name (must match the model used
                                at index time — mismatched models give bad results).
        chroma_persist_dir:     Path to Chroma's local storage.
        chroma_collection_name: Name of the Chroma collection to search.
        top_k:                  Number of chunks to retrieve.
        document_ids:           Optional filter — restrict search to these docs.

    Returns:
        Ranked list of SearchResult objects (best match first).
    """
    logger.info("Retrieving top-%d chunks for question: %.80s...", top_k, question)

    query_embedding = embed_query(question, embedding_model)
    results = similarity_search(
        query_embedding=query_embedding,
        top_k=top_k,
        persist_dir=chroma_persist_dir,
        collection_name=chroma_collection_name,
        document_ids=document_ids,
    )

    logger.debug("Retrieved %d chunks", len(results))
    return results
