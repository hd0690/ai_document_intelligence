"""Configuration management for Document Intelligence Tool."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_embedding_model: str = "nomic-embed-text"
    ollama_llm_model: str = "llama3.2"

    # Database Configuration
    chroma_db_path: str = "./data/chroma_db"
    chroma_collection_name: str = "documents"

    # Application Settings
    debug: bool = False
    log_level: str = "INFO"
    log_file: str = "./logs/queries.log"

    # Document Processing
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k_retrieval: int = 5

    # Paths
    data_dir: Path = Path(__file__).parent / "data"
    docs_dir: Path = Path(__file__).parent / "data" / "docs"
    logs_dir: Path = Path(__file__).parent / "logs"

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def __init__(self, **data):
        """Initialize settings and create necessary directories."""
        super().__init__(**data)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        Path(self.chroma_db_path).mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
