"""Application configuration.

All configuration is read from environment variables (optionally loaded from
a `.env` file at the repository root) via Pydantic Settings. Nothing in the
application should read `os.environ` directly — everything flows through the
`Settings` model so configuration stays centralized, typed, and validated.
"""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# apps/backend/app/core/config.py -> repo root is three levels up.
_REPO_ROOT = Path(__file__).resolve().parents[3]
_ROOT_ENV_FILE = _REPO_ROOT / ".env"


class Environment(StrEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class Settings(BaseSettings):
    """Typed application configuration.

    Defaults mirror `.env.example` so the application can boot locally
    without a `.env` file present. Real deployments override every value
    via environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=str(_ROOT_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Shared ---
    environment: Environment = Environment.DEVELOPMENT

    # --- API ---
    api_version: str = "v1"
    project_name: str = "Pit Wall Insight"

    # --- CORS (docs/05_BACKEND_ARCHITECTURE.md, middleware responsibilities) ---
    # Vite's default dev port (5173) and preview port (4173) — the frontend
    # (apps/frontend) has no proxy/rewrite configured, so it calls this API
    # directly from the browser and needs an explicit CORS allowance.
    # Comma-separated in the environment; production deployments override
    # with the real deployed frontend origin(s).
    cors_origins: str = "http://localhost:5173,http://localhost:4173"

    # --- Database (raw/bronze + analytics/gold, see docs/07_DATABASE_SCHEMA.md) ---
    database_url: str = "postgresql://pitwall:pitwall@localhost:5432/pit_wall_insight_raw"
    analytics_database_url: str = (
        "postgresql://pitwall:pitwall@localhost:5432/pit_wall_insight_analytics"
    )

    # --- Security ---
    secret_key: str = "change-me-in-production"

    # --- Logging ---
    log_level: str = "info"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def api_prefix(self) -> str:
        return f"/api/{self.api_version}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sqlalchemy_database_uri(self) -> str:
        """`database_url` adapted for SQLAlchemy's async engine (asyncpg driver)."""
        return _with_asyncpg_driver(self.database_url)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def analytics_sqlalchemy_database_uri(self) -> str:
        return _with_asyncpg_driver(self.analytics_database_url)


def _with_asyncpg_driver(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance, safe to use as a FastAPI dependency."""
    return Settings()
