"""
Query service: delegates to the RAG pipeline.

Kept as a thin service layer so the API route stays clean and this logic
remains independently testable without spinning up HTTP.
"""

from app.config import Settings
from app.core.rag.pipeline import run_rag_pipeline
from app.models.query import QueryRequest, QueryResponse


def answer_question(request: QueryRequest, settings: Settings) -> QueryResponse:
    """
    Execute the RAG pipeline for a user question.

    Args:
        request:  Validated QueryRequest (question, optional filters, top_k).
        settings: Application settings.

    Returns:
        QueryResponse with the LLM's answer and source citations.
    """
    return run_rag_pipeline(
        question=request.question,
        settings=settings,
        top_k=request.top_k,
        document_ids=request.document_ids,
    )
