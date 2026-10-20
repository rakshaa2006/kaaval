"""Kaaval application configuration.

Settings are loaded from environment variables (and an optional .env file).
All values are validated by Pydantic Settings at startup.
"""
from __future__ import annotations

from enum import Enum
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(str, Enum):
    SYNTHETIC_DEMO = "SYNTHETIC_DEMO"
    STAGING = "STAGING"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Environment ───────────────────────────────────────────────────────────
    app_env: AppEnv = AppEnv.SYNTHETIC_DEMO

    # ── Database ──────────────────────────────────────────────────────────────
    database_url: str = "sqlite:///./kaaval.db"


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton Settings instance."""
    return Settings()
