"""Insights endpoints — placeholder for Phase 3 (summarization, extraction)."""

from fastapi import APIRouter

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/health")
def insights_health() -> dict:
    return {"status": "Insights endpoints coming in Phase 3"}
