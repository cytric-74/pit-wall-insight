"""SQLAlchemy ORM models.

Re-exports every model so `Base.metadata` (see `app/database/session.py`)
sees the full schema as soon as `app.models` is imported anywhere — Alembic
autogenerate, `Base.metadata.create_all()` in tests, and any future code all
rely on that side effect rather than each having to remember which model
modules to import individually.

Currently only the Bronze/raw layer (`app/models/raw/`) exists — see
docs/07_DATABASE_SCHEMA.md for the planned Gold layer (`dim_*`/`fct_*`/
`mart_*`), which is a future phase.
"""

from app.models.raw import (
    RawCircuit,
    RawConstructor,
    RawDriver,
    RawLap,
    RawResult,
    RawSession,
    RawWeather,
)

__all__ = [
    "RawCircuit",
    "RawConstructor",
    "RawDriver",
    "RawLap",
    "RawResult",
    "RawSession",
    "RawWeather",
]
