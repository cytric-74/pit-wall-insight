"""SQLAlchemy ORM models.

Re-exports every model so `Base.metadata`/`GoldBase.metadata` (see
`app/database/session.py`) see the full schema as soon as `app.models` is
imported anywhere — Alembic autogenerate (both `alembic/` for raw and
`alembic_gold/` for gold), `Base.metadata.create_all()`/
`GoldBase.metadata.create_all()` in tests, and any future code all rely on
that side effect rather than each having to remember which model modules
to import individually.

Raw (`app/models/raw/`) and Gold (`app/models/gold/`) models attach to two
separate declarative bases with two separate `metadata` objects, even
though both are imported here — importing this module is what makes
either metadata "complete," but which of the two a given Alembic
environment or test actually acts on depends on which `Base` it reads
(see `alembic/env.py` vs `alembic_gold/env.py`).

Marts (`mart_*`) remain a future phase — see docs/07_DATABASE_SCHEMA.md.
"""

from app.models.gold import (
    DimCircuit,
    DimConstructor,
    DimDriver,
    DimSeason,
    DimSession,
    DimWeather,
    FctLap,
    FctPitstop,
    FctResult,
)
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
    "DimCircuit",
    "DimConstructor",
    "DimDriver",
    "DimSeason",
    "DimSession",
    "DimWeather",
    "FctLap",
    "FctPitstop",
    "FctResult",
    "RawCircuit",
    "RawConstructor",
    "RawDriver",
    "RawLap",
    "RawResult",
    "RawSession",
    "RawWeather",
]
