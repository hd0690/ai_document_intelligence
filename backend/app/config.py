from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Environment ───────────────────────────────────────────────────────────
    app_env: str = "development"
    log_level: str = "INFO"

    # ── LLM ──────────────────────────────────────────────────────────────────
    llm_provider: str = "ollama"  # "ollama" | "openrouter"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-4o-mini"

    # ── Embeddings ────────────────────────────────────────────────────────────
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # ── Chroma ────────────────────────────────────────────────────────────────
    chroma_persist_dir: str = "./storage/chroma_db"
    chroma_collection_name: str = "documents"

    # ── Storage ───────────────────────────────────────────────────────────────
    upload_dir: str = "./storage/uploads"
    processed_dir: str = "./storage/processed"

    # ── RAG ───────────────────────────────────────────────────────────────────
    rag_top_k: int = 5
    chunk_size: int = 512
    chunk_overlap: int = 64

    @field_validator("llm_provider")
    @classmethod
    def validate_llm_provider(cls, v: str) -> str:
        allowed = {"ollama", "openrouter"}
        if v not in allowed:
            raise ValueError(f"llm_provider must be one of {allowed}, got '{v}'")
        return v

    def ensure_dirs(self) -> None:
        """Create storage directories if they don't exist."""
        for dir_path in (self.upload_dir, self.processed_dir, self.chroma_persist_dir):
            Path(dir_path).mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance. Import and call this everywhere."""
    settings = Settings()
    settings.ensure_dirs()
    return settings
