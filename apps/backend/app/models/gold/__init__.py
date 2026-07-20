"""Gold-layer (`dim_*`/`fct_*`/`mart_*`) SQLAlchemy ORM models (docs/07_DATABASE_SCHEMA.md).

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

Marts (`mart_dashboard`, `mart_driver_summary`, `mart_constructor_summary`,
`mart_race_summary`) sit on top of the dimensions/facts above — aggregated,
business-ready views a dashboard or API endpoint reads directly rather than
computing the same joins/aggregations itself on every request. Two of them
(`mart_driver_summary`, `mart_constructor_summary`) add a `season_id` scope
beyond docs/07's literal column list — see those models' docstrings for
why. Still out of scope (deferred, consistent with every earlier phase):
anything telemetry- or strategy-related (`fct_telemetry`,
`mart_strategy_analysis`, `mart_telemetry_summary`).
"""

from app.models.gold.circuit import DimCircuit
from app.models.gold.constructor import DimConstructor
from app.models.gold.driver import DimDriver
from app.models.gold.lap import FctLap
from app.models.gold.mart_constructor_summary import MartConstructorSummary
from app.models.gold.mart_dashboard import MartDashboard
from app.models.gold.mart_driver_summary import MartDriverSummary
from app.models.gold.mart_race_summary import MartRaceSummary
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
    "MartConstructorSummary",
    "MartDashboard",
    "MartDriverSummary",
    "MartRaceSummary",
]
