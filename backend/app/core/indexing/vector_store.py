"""
Vector store: persistent Chroma wrapper.

Responsibilities:
  - Add chunks (text + embedding + metadata) for a document
  - Query by embedding similarity
  - Delete all chunks belonging to a document
  - List distinct document IDs stored in the collection

Design notes:
  - One Chroma collection holds ALL documents.
  - Each chunk is stored as a separate Chroma document.
  - document_id and filename are stored in metadata so we can filter and
    surface citations at query time.
  - Chroma IDs are deterministic: "{document_id}_chunk_{chunk_index}" — this
    makes upserts idempotent (re-indexing the same file doesn't duplicate data).
"""

import logging
from dataclasses import dataclass
from functools import lru_cache

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    chunk_text: str
    document_id: str
    filename: str
    score: float        # cosine distance (lower = more similar); Chroma returns distance
    chunk_index: int


@lru_cache(maxsize=1)
def _get_chroma_collection(persist_dir: str, collection_name: str):
    """Create/load Chroma collection (cached — one instance per process)."""
    try:
        import chromadb
    except ImportError as e:
        raise RuntimeError("chromadb is not installed. Run: uv add chromadb") from e

    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},   # cosine similarity for text embeddings
    )
    logger.info(
        "Chroma collection '%s' ready at %s (existing items: %d)",
        collection_name,
        persist_dir,
        collection.count(),
    )
    return collection


def add_chunks(
    document_id: str,
    filename: str,
    chunk_texts: list[str],
    embeddings: list[list[float]],
    persist_dir: str,
    collection_name: str,
) -> None:
    """
    Upsert all chunks for a document into Chroma.

    Using upsert (not add) so re-indexing the same document is safe.
    """
    if len(chunk_texts) != len(embeddings):
        raise ValueError("chunk_texts and embeddings must have the same length")

    collection = _get_chroma_collection(persist_dir, collection_name)

    ids = [f"{document_id}_chunk_{i}" for i in range(len(chunk_texts))]
    metadatas = [
        {"document_id": document_id, "filename": filename, "chunk_index": i}
        for i in range(len(chunk_texts))
    ]

    collection.upsert(
        ids=ids,
        documents=chunk_texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    logger.info("Upserted %d chunks for document '%s'", len(chunk_texts), document_id)


def similarity_search(
    query_embedding: list[float],
    top_k: int,
    persist_dir: str,
    collection_name: str,
    document_ids: list[str] | None = None,
) -> list[SearchResult]:
    """
    Retrieve the top-k most similar chunks for a query embedding.

    Args:
        query_embedding: Embedding vector for the user's question.
        top_k:           Number of results to return.
        persist_dir:     Chroma persistence directory.
        collection_name: Chroma collection name.
        document_ids:    Optional filter — restrict to chunks from these documents.
    """
    collection = _get_chroma_collection(persist_dir, collection_name)

    where_filter = (
        {"document_id": {"$in": document_ids}} if document_ids else None
    )

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count() or 1),
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    search_results: list[SearchResult] = []
    for text, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        search_results.append(
            SearchResult(
                chunk_text=text,
                document_id=meta["document_id"],
                filename=meta["filename"],
                score=float(distance),
                chunk_index=meta["chunk_index"],
            )
        )

    return search_results


def delete_document(
    document_id: str,
    persist_dir: str,
    collection_name: str,
) -> None:
    """Remove all chunks for a given document from the collection."""
    collection = _get_chroma_collection(persist_dir, collection_name)
    collection.delete(where={"document_id": {"$eq": document_id}})
    logger.info("Deleted all chunks for document '%s'", document_id)


def list_document_ids(persist_dir: str, collection_name: str) -> list[str]:
    """Return distinct document IDs present in the collection."""
    collection = _get_chroma_collection(persist_dir, collection_name)
    if collection.count() == 0:
        return []

    # Fetch all metadatas (no embeddings needed)
    all_items = collection.get(include=["metadatas"])
    seen: set[str] = set()
    for meta in all_items["metadatas"]:
        seen.add(meta["document_id"])
    return sorted(seen)
