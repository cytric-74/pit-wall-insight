"""Response DTOs for `/strategy/tyres` (docs/08_API_SPECIFICATION.md — "Strategy").

Only tyre degradation is built in this phase — `/strategy/undercut`,
`/strategy/overcut`, and `/strategy/simulation` all need pit-stop-timing
data more complete than Phase 4's known `fct_pitstop` gap allows (see
`app/models/gold/pitstop.py`), and `/strategy` itself ("season strategies")
isn't well-defined beyond what `/races/{id}/strategy` and this endpoint
already cover.
"""

from __future__ import annotations

from app.schemas.base import CamelModel


class TyreDegradationPoint(CamelModel):
    compound: str
    tyre_life: float
    average_lap_time: float
    sample_count: int


class TyreDegradation(CamelModel):
    points: list[TyreDegradationPoint]
