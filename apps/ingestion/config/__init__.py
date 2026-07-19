"""Configuration for the ingestion pipeline.

Mirrors the pattern used by `apps/backend/app/core/config.py` (typed,
env-driven settings via Pydantic Settings, cached with `@lru_cache`) so the
two independently-deployable apps in this monorepo stay consistent, without
either one importing code from the other — per `docs/04_FRONTEND_ARCHITECTURE.md`
/ `docs/06_DATA_ENGINEERING.md`, `apps/ingestion` and `apps/backend` are
separate deployables with their own dependency sets and lifecycles.
"""
