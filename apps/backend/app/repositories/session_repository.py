"""Read-only Gold-layer queries backing `/sessions*` (docs/08_API_SPECIFICATION.md).

Not to be confused with `app.database.session` (the SQLAlchemy engine/
session module) — this queries `dim_session`, the Gold dimension for one
(season, round, session_type) combination.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Row, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    DimCircuit,
    DimConstructor,
    DimDriver,
    DimSeason,
    DimSession,
    FctLap,
    FctResult,
)


async def get_session_by_id(session: AsyncSession, session_id: uuid.UUID) -> Row[Any] | None:
    statement = (
        select(
            DimSession.session_id,
            DimSeason.year.label("season"),
            DimSession.round_number.label("round"),
            DimSession.race_name,
            DimSession.session_type,
            DimCircuit.name.label("circuit"),
            DimSession.date,
        )
        .join(DimSeason, DimSeason.season_id == DimSession.season_id)
        .outerjoin(DimCircuit, DimCircuit.circuit_id == DimSession.circuit_id)
        .where(DimSession.session_id == session_id)
    )
    result = await session.execute(statement)
    return result.first()


async def session_exists(session: AsyncSession, session_id: uuid.UUID) -> bool:
    result = await session.execute(
        select(DimSession.session_id).where(DimSession.session_id == session_id)
    )
    return result.first() is not None


async def list_results(session: AsyncSession, session_id: uuid.UUID) -> list[Row[Any]]:
    statement = (
        select(
            DimDriver.full_name.label("driver"),
            DimConstructor.team_name.label("team"),
            FctResult.grid_position,
            FctResult.finish_position,
            FctResult.points,
            FctResult.status,
            FctResult.fastest_lap,
            FctResult.laps_completed,
        )
        .join(DimDriver, DimDriver.driver_id == FctResult.driver_id)
        .outerjoin(DimConstructor, DimConstructor.constructor_id == DimDriver.team_id)
        .where(FctResult.session_id == session_id)
        .order_by(FctResult.finish_position)
    )
    result = await session.execute(statement)
    return list(result.all())


async def list_laps(session: AsyncSession, session_id: uuid.UUID) -> list[Row[Any]]:
    statement = (
        select(
            DimDriver.full_name.label("driver"),
            FctLap.lap_number,
            FctLap.lap_time,
            FctLap.compound,
            FctLap.tyre_life,
            FctLap.position,
            FctLap.pit_in,
            FctLap.pit_out,
        )
        .join(DimDriver, DimDriver.driver_id == FctLap.driver_id)
        .where(FctLap.session_id == session_id)
        .order_by(DimDriver.full_name, FctLap.lap_number)
    )
    result = await session.execute(statement)
    return list(result.all())
