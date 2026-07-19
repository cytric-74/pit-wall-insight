"""Bronze-layer (raw_*) SQLAlchemy ORM models (docs/07_DATABASE_SCHEMA.md, docs/06_DATA_ENGINEERING.md).

Purpose
-------
Represents the Bronze layer of the warehouse: raw, immutable, source-aligned
data, one table per entity the ingestion pipeline collects. Every model
here is deliberately "dumb" — plain columns, no computed properties, no
relationships that would encourage querying across entities at this layer.
docs/06_DATA_ENGINEERING.md is explicit that only the Gold layer (a future
phase: `dim_*`, `fct_*`, `mart_*`) is meant to be queried for analytics;
these tables exist purely so `apps/ingestion`'s loaders have somewhere
durable and reproducible to write validated records.

Two upstream sources (FastF1 and Jolpica-F1/Ergast) sometimes describe the
same real-world entity (e.g. session results for the same race). Bronze
tables never merge or reconcile these — every row is tagged with its
`source` (see `AuditMixin`), and multiple rows for what is conceptually
"the same" result/session can and do coexist side by side. Deciding which
source to prefer, or how to combine them, is Gold-layer transformation
logic for a future phase, not something a Bronze table encodes.

Why these tables don't exactly mirror every raw source field 1:1: nested
objects a source returns (e.g. Jolpica's `Driver`/`Constructor`/`Circuit`
sub-objects, embedded inside standings and results payloads) are extracted
into their own tables here (`RawDriver`, `RawConstructor`, `RawCircuit`)
rather than duplicated inline on every row that references them — still
"minimal transformation" in spirit (no values are computed or changed,
only de-duplicated by natural key), and it's what makes idempotent
re-ingestion meaningful (a driver seen in a hundred different results rows
across a season is still one row here, upserted by natural key each time).

Out of scope this phase (see docs/07_DATABASE_SCHEMA.md's full list):
`raw_telemetry` and pit-stop-specific tables — telemetry and strategy
analytics are a deferred future phase; `RawLap` already carries the
`pit_in_time`/`pit_out_time` columns a future phase's `fct_pitstop`
transform will derive pit stops from, so no separate raw pit-stop table is
needed at this grain.
"""

from app.models.raw.circuit import RawCircuit
from app.models.raw.constructor import RawConstructor
from app.models.raw.driver import RawDriver
from app.models.raw.lap import RawLap
from app.models.raw.result import RawResult
from app.models.raw.session import RawSession
from app.models.raw.weather import RawWeather

__all__ = [
    "RawCircuit",
    "RawConstructor",
    "RawDriver",
    "RawLap",
    "RawResult",
    "RawSession",
    "RawWeather",
]
