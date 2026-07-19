"""Gold-layer (`dim_*`/`fct_*`) SQLAlchemy ORM models (docs/07_DATABASE_SCHEMA.md).

Purpose
-------
The analytics-ready star schema — the only layer `apps/backend`'s future
API routes/repositories are allowed to query (docs/06_DATA_ENGINEERING.md
Decision 005: "API Reads Only Gold Models"). Every row here is *derived*
from Bronze (`app/models/raw/`), never collected directly from FastF1 or
Jolpica — that derivation lives in
`apps/ingestion/transformers/bronze_to_gold.py`, following the same
"no cross-app import" architecture as the Bronze loaders (see
`apps/ingestion/loaders/bronze_loader.py`'s module docstring): the
transformer reflects both the raw and gold tables at runtime rather than
importing these classes.

Unlike Bronze, Gold tables *do* reconcile across sources (FastF1 vs.
Jolpica) and *do* enforce foreign keys between each other — that's the
entire point of this layer: turning "two sources' worth of raw, possibly
overlapping rows" into one coherent, query-ready structure. Every foreign
key in this package points at another Gold table, never at Bronze.

Primary keys use the entity-specific names docs/07_DATABASE_SCHEMA.md's
"Naming Convention" section mandates (`driver_id`, `constructor_id`,
`season_id`, ...) rather than Bronze's generic `id` — see
`app/models/mixins.py` for why that split exists.

Out of scope this phase (deferred, see docs/07_DATABASE_SCHEMA.md's full
list): `mart_*` tables (aggregated, business-ready views built on top of
these dimensions/facts — a distinct, later phase) and anything telemetry-
or strategy-related (`fct_telemetry`, `mart_strategy_analysis`,
`mart_telemetry_summary`), consistent with earlier phases' scope.
"""

from app.models.gold.circuit import DimCircuit
from app.models.gold.constructor import DimConstructor
from app.models.gold.driver import DimDriver
from app.models.gold.lap import FctLap
from app.models.gold.pitstop import FctPitstop
from app.models.gold.result import FctResult
from app.models.gold.season import DimSeason
from app.models.gold.session import DimSession
from app.models.gold.weather import DimWeather

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
]
