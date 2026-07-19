"""Typed, environment-driven configuration for the ingestion pipeline.

Purpose
-------
Every value the ingestion pipeline needs at runtime (where to cache FastF1
sessions, which Jolpica/Ergast host to call, how long to wait on a slow
upstream request, which pipeline version to stamp onto records) is declared
here as a single `Settings` model, following the exact same rationale as
`apps/backend/app/core/config.py`: nothing in this codebase should read
`os.environ` directly, because that scatters configuration knowledge across
the codebase and makes it impossible to know, from one place, what the
pipeline actually depends on to run.

Inputs
------
Environment variables, optionally loaded from a `.env` file at the
repository root (the same `.env` the frontend and backend both read from —
see `.env.example`). Every field has a sensible development default so the
pipeline can run with zero configuration; production deployments override
via real environment variables.

Outputs
-------
`get_settings()` returns a cached `Settings` instance. Because it's
decorated with `@lru_cache`, repeated calls return the *same* object rather
than re-reading the environment every time, which matters here because
`collectors/fastf1_client.py` uses the returned settings to decide whether
the on-disk FastF1 cache has already been enabled for this process.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# apps/ingestion/config/settings.py -> repository root is two levels up.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_ROOT_ENV_FILE = _REPO_ROOT / ".env"


class Settings(BaseSettings):
    """Typed configuration for the ingestion pipeline.

    Field defaults intentionally mirror `.env.example` so a fresh checkout
    can run `python main.py` immediately, without requiring a `.env` file —
    the same design constraint `apps/backend/app/core/config.py` documents.
    """

    model_config = SettingsConfigDict(
        env_file=str(_ROOT_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- FastF1 ---
    # Directory FastF1 uses to cache downloaded session data on disk. FastF1
    # sessions are large (multi-megabyte) and slow to fetch from the live
    # timing API, so caching isn't an optimization here — without it, every
    # run would re-download identical historical data that never changes.
    fastf1_cache: str = "./.fastf1_cache"

    # --- Jolpica-F1 (Ergast-compatible historical data) ---
    # Ergast's own API (ergast.com) was retired in 2024; Jolpica-F1 is the
    # community-run, byte-compatible successor — same JSON shape, same
    # endpoints, no API key required. See collectors/ergast_client.py.
    jolpica_base_url: str = "https://api.jolpi.ca/ergast/f1"

    # --- HTTP behavior ---
    # Applied to every outbound Jolpica request. A generous but finite
    # timeout: F1 historical data endpoints are not latency-sensitive, but
    # an unbounded timeout would let one unreachable upstream hang the
    # entire pipeline run indefinitely.
    request_timeout_seconds: float = 15.0
    # Identifies this pipeline to upstream APIs. Jolpica-F1's own
    # documentation asks integrators to send a descriptive User-Agent so
    # they can contact maintainers of misbehaving clients — sending the
    # default `python-requests/x.y` string is inconsiderate to a free,
    # community-run service.
    user_agent: str = "pit-wall-insight-ingestion/0.1 (+https://github.com/pit-wall-insight)"

    # --- Bronze/raw database (docs/06_DATA_ENGINEERING.md "API Reads Only
    # Gold Models" — ingestion writes to the *other* side of that split).
    # Same connection string apps/backend's `DATABASE_URL` resolves to
    # (both read the same root `.env`), but with a plain `postgresql://`
    # URL rather than backend's `+asyncpg` variant — this pipeline uses a
    # sync SQLAlchemy engine (see `loaders/bronze_loader.py`), matching the
    # sync `psycopg` driver in requirements.txt.
    database_url: str = "postgresql://pitwall:pitwall@localhost:5432/pit_wall_insight_raw"

    # --- Pipeline metadata (docs/06_DATA_ENGINEERING.md "Metadata") ---
    # Stamped onto every record this pipeline persists, so any row in the
    # warehouse can be traced back to the exact pipeline version that
    # produced it (docs/06: "This enables reproducibility.").
    pipeline_version: str = "0.1.0"

    # --- Logging ---
    log_level: str = "info"


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide `Settings` instance, constructed once.

    Time complexity: O(1) after the first call — `lru_cache` memoizes the
    result of the (otherwise environment-and-file-reading) construction.
    Safe to call from anywhere in the ingestion package; it never re-reads
    the environment mid-process, so settings are stable for the lifetime of
    a single pipeline run even if the environment changes underneath it.
    """
    return Settings()
