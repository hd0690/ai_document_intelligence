import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import documents, insights, query
from app.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Document Intelligence API",
        description="AI-powered document ingestion, RAG, and insights system.",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS — open for local dev; tighten in production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.app_env == "development" else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────────────────
    api_prefix = "/api/v1"
    app.include_router(documents.router, prefix=api_prefix)
    app.include_router(query.router, prefix=api_prefix)
    app.include_router(insights.router, prefix=api_prefix)

    # ── Health check ──────────────────────────────────────────────────────────
    @app.get("/health", tags=["health"])
    def health() -> dict:
        return {"status": "ok", "env": settings.app_env, "llm_provider": settings.llm_provider}

    logger.info("App created (env=%s, llm=%s)", settings.app_env, settings.llm_provider)
    return app


app = create_app()
