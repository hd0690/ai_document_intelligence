"""Logging utilities for Document Intelligence Tool."""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from config import settings


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Set up a logger with console and file handlers.

    Args:
        name: Logger name
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_format)

    # File handler
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(console_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def log_query(
    query: str,
    retrieved_chunks: list[str],
    final_prompt: str,
    response: str | None = None,
) -> None:
    """
    Log a query to the JSON log file.

    Args:
        query: User's query
        retrieved_chunks: List of retrieved document chunks
        final_prompt: Final prompt sent to LLM
        response: LLM's response (optional)
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "query": query,
        "retrieved_chunks": retrieved_chunks,
        "final_prompt": final_prompt,
        "response": response,
    }

    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger instance."""
    return logging.getLogger(name)
