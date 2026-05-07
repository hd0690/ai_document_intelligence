import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import Settings
from app.dependencies import get_app_settings
from app.models.query import QueryRequest, QueryResponse
from app.services.query_service import answer_question

router = APIRouter(prefix="/query", tags=["query"])
logger = logging.getLogger(__name__)


@router.post("", response_model=QueryResponse)
def query_documents(
    request: QueryRequest,
    settings: Settings = Depends(get_app_settings),
) -> QueryResponse:
    """
    Ask a natural-language question over indexed documents.

    Returns the LLM's answer along with the source chunks used as context.
    """
    try:
        return answer_question(request, settings)
    except Exception as exc:
        logger.exception("Query pipeline failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {exc}",
        ) from exc
