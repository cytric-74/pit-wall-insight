"""Read-only Gold-layer queries backing `/strategy/tyres` (docs/08_API_SPECIFICATION.md)."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Row, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DimSeason, DimSession, FctLap


async def get_tyre_degradation(
    session: AsyncSession,
    *,
    season: int | None,
    driver_id: uuid.UUID | None,
    round_number: int | None,
    session_type: str | None,
) -> list[Row[Any]]:
    """Average lap time per (compound, tyre_life) — in-lap/out-lap laps are
    excluded, since a pit lap's time reflects entering/exiting the pits, not
    tyre performance.
    """
    statement = (
        select(
            FctLap.compound,
            FctLap.tyre_life,
            func.avg(FctLap.lap_time).label("average_lap_time"),
            func.count().label("sample_count"),
        )
        .join(DimSession, DimSession.session_id == FctLap.session_id)
        .join(DimSeason, DimSeason.season_id == DimSession.season_id)
        .where(
            FctLap.lap_time.is_not(None),
            FctLap.compound.is_not(None),
            FctLap.tyre_life.is_not(None),
            FctLap.pit_in.is_(False),
            FctLap.pit_out.is_(False),
        )
    )
    if season is not None:
        statement = statement.where(DimSeason.year == season)
    if driver_id is not None:
        statement = statement.where(FctLap.driver_id == driver_id)
    if round_number is not None:
        statement = statement.where(DimSession.round_number == round_number)
    if session_type is not None:
        statement = statement.where(DimSession.session_type == session_type)

    statement = statement.group_by(FctLap.compound, FctLap.tyre_life).order_by(
        FctLap.compound, FctLap.tyre_life
    )
    result = await session.execute(statement)
    return list(result.all())
