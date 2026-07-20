"""Read-only Gold-layer queries backing `/circuits*` (docs/08_API_SPECIFICATION.md)."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Row, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DimCircuit, DimDriver, DimSeason, DimSession, FctLap, MartRaceSummary

_RACE_SESSION_TYPE = "R"


async def list_circuits(
    session: AsyncSession, *, page: int, limit: int
) -> tuple[list[DimCircuit], int]:
    total = (await session.execute(select(func.count()).select_from(DimCircuit))).scalar_one()
    result = await session.execute(
        select(DimCircuit).order_by(DimCircuit.name).offset((page - 1) * limit).limit(limit)
    )
    return list(result.scalars().all()), total


async def get_circuit_by_id(session: AsyncSession, circuit_id: uuid.UUID) -> DimCircuit | None:
    result = await session.execute(
        select(DimCircuit).where(DimCircuit.circuit_id == circuit_id)
    )
    return result.scalar_one_or_none()


async def list_race_history(session: AsyncSession, circuit_id: uuid.UUID) -> list[Row[Any]]:
    """Every race run at this circuit, most recent first."""
    statement = (
        select(
            DimSeason.year.label("season"),
            DimSession.round_number.label("round"),
            DimSession.race_name.label("race_name"),
            MartRaceSummary.winner,
            MartRaceSummary.pole,
            MartRaceSummary.fastest_lap,
        )
        .join(DimSeason, DimSeason.season_id == DimSession.season_id)
        .outerjoin(MartRaceSummary, MartRaceSummary.session_id == DimSession.session_id)
        .where(DimSession.circuit_id == circuit_id, DimSession.session_type == _RACE_SESSION_TYPE)
        .order_by(DimSeason.year.desc(), DimSession.round_number.desc())
    )
    result = await session.execute(statement)
    return list(result.all())


async def get_track_record(session: AsyncSession, circuit_id: uuid.UUID) -> Row[Any] | None:
    """The fastest lap ever recorded at this circuit, across every loaded season."""
    statement = (
        select(
            DimDriver.full_name.label("driver"),
            FctLap.lap_time,
            DimSeason.year.label("season"),
            DimSession.round_number.label("round"),
        )
        .join(DimSession, DimSession.session_id == FctLap.session_id)
        .join(DimSeason, DimSeason.season_id == DimSession.season_id)
        .join(DimDriver, DimDriver.driver_id == FctLap.driver_id)
        .where(DimSession.circuit_id == circuit_id, FctLap.lap_time.is_not(None))
        .order_by(FctLap.lap_time)
        .limit(1)
    )
    result = await session.execute(statement)
    return result.first()
