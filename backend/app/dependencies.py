"""
FastAPI dependency injection.

Functions here are used with `Depends()` in route handlers so that:
  - Settings are loaded once and cached
  - Swapping implementations in tests requires changing only one place
"""

from app.config import Settings, get_settings


def get_app_settings() -> Settings:
    """Provides the application settings (cached singleton)."""
    return get_settings()
