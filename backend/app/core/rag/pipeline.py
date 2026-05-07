"""
RAG pipeline: orchestrates retrieval → generation in one call.

This is the main entry point for the query flow:
  1. Retrieve relevant chunks from the vector store
  2. Pass chunks as context to the LLM
  3. Return the answer and the source chunks (for citations)

The pipeline takes a Settings object so it works the same way in tests
(inject a test config) and in production (inject the real config).
"""

import logging

from app.config import Settings
from app.core.rag.generator import generate_answer
from app.core.rag.retriever import retrieve
from app.models.query import QueryResponse, SourceChunk

logger = logging.getLogger(__name__)


def run_rag_pipeline(
    question: str,
    settings: Settings,
    top_k: int | None = None,
    document_ids: list[str] | None = None,
) -> QueryResponse:
    """
    End-to-end RAG: retrieve relevant chunks then generate an LLM answer.

    Args:
        question:     The user's natural-language question.
        settings:     Application settings (LLM provider, model names, paths…).
        top_k:        Override the default retrieval count from settings.
        document_ids: Optionally restrict search to these document IDs.

    Returns:
        QueryResponse with the answer and source chunk citations.
    """
    effective_top_k = top_k if top_k is not None else settings.rag_top_k

    # Step 1 — Retrieve
    results = retrieve(
        question=question,
        embedding_model=settings.embedding_model,
        chroma_persist_dir=settings.chroma_persist_dir,
        chroma_collection_name=settings.chroma_collection_name,
        top_k=effective_top_k,
        document_ids=document_ids,
    )

    # Step 2 — Generate
    context_chunks = [r.chunk_text for r in results]
    answer = generate_answer(
        question=question,
        context_chunks=context_chunks,
        llm_provider=settings.llm_provider,
        ollama_base_url=settings.ollama_base_url,
        ollama_model=settings.ollama_model,
        openrouter_api_key=settings.openrouter_api_key,
        openrouter_model=settings.openrouter_model,
    )

    # Step 3 — Build response with citations
    sources = [
        SourceChunk(
            document_id=r.document_id,
            filename=r.filename,
            chunk_text=r.chunk_text,
            score=r.score,
        )
        for r in results
    ]

    logger.info("RAG pipeline complete. Sources used: %d", len(sources))
    return QueryResponse(question=question, answer=answer, sources=sources)
