"""Read-only Gold-layer queries backing `/races*` (docs/08_API_SPECIFICATION.md).

A "race" is `dim_session` scoped to `session_type == "R"` — see
`app/schemas/race.py` for why there's no separate race entity.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Row, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    DimCircuit,
    DimDriver,
    DimSeason,
    DimSession,
    DimWeather,
    FctLap,
    FctPitstop,
    MartRaceSummary,
)

_RACE_SESSION_TYPE = "R"


async def list_races(
    session: AsyncSession,
    *,
    season: int | None,
    country: str | None,
    page: int,
    limit: int,
) -> tuple[list[Row[Any]], int]:
    statement = (
        select(
            DimSession.session_id,
            DimSeason.year.label("season"),
            DimSession.round_number.label("round"),
            DimSession.race_name,
            DimCircuit.name.label("circuit"),
            DimCircuit.country,
            DimSession.date,
            MartRaceSummary.winner,
        )
        .join(DimSeason, DimSeason.season_id == DimSession.season_id)
        .outerjoin(DimCircuit, DimCircuit.circuit_id == DimSession.circuit_id)
        .outerjoin(MartRaceSummary, MartRaceSummary.session_id == DimSession.session_id)
        .where(DimSession.session_type == _RACE_SESSION_TYPE)
    )
    if season is not None:
        statement = statement.where(DimSeason.year == season)
    if country is not None:
        statement = statement.where(DimCircuit.country == country)

    total = (
        await session.execute(select(func.count()).select_from(statement.subquery()))
    ).scalar_one()

    statement = (
        statement.order_by(DimSeason.year.desc(), DimSession.round_number.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    result = await session.execute(statement)
    return list(result.all()), total


async def get_race_by_id(session: AsyncSession, session_id: uuid.UUID) -> Row[Any] | None:
    statement = (
        select(
            DimSession.session_id,
            DimSeason.year.label("season"),
            DimSession.round_number.label("round"),
            DimSession.race_name,
            DimCircuit.name.label("circuit"),
            DimCircuit.country,
            DimSession.date,
            MartRaceSummary.winner,
            MartRaceSummary.pole,
            MartRaceSummary.fastest_lap,
            MartRaceSummary.retirements,
            MartRaceSummary.weather,
            MartRaceSummary.average_pitstop,
        )
        .join(DimSeason, DimSeason.season_id == DimSession.season_id)
        .outerjoin(DimCircuit, DimCircuit.circuit_id == DimSession.circuit_id)
        .outerjoin(MartRaceSummary, MartRaceSummary.session_id == DimSession.session_id)
        .where(DimSession.session_id == session_id, DimSession.session_type == _RACE_SESSION_TYPE)
    )
    result = await session.execute(statement)
    return result.first()


async def list_positions(session: AsyncSession, session_id: uuid.UUID) -> list[Row[Any]]:
    statement = (
        select(
            DimDriver.full_name.label("driver"),
            FctLap.lap_number,
            FctLap.position,
        )
        .join(DimDriver, DimDriver.driver_id == FctLap.driver_id)
        .where(FctLap.session_id == session_id)
        .order_by(DimDriver.full_name, FctLap.lap_number)
    )
    result = await session.execute(statement)
    return list(result.all())


async def list_pitstops(session: AsyncSession, session_id: uuid.UUID) -> list[Row[Any]]:
    statement = (
        select(
            DimDriver.full_name.label("driver"),
            FctPitstop.lap,
            FctPitstop.pit_duration,
            FctPitstop.stop_number,
            FctPitstop.compound_before,
            FctPitstop.compound_after,
        )
        .join(DimDriver, DimDriver.driver_id == FctPitstop.driver_id)
        .where(FctPitstop.session_id == session_id)
        .order_by(FctPitstop.lap)
    )
    result = await session.execute(statement)
    return list(result.all())


async def get_weather(session: AsyncSession, session_id: uuid.UUID) -> DimWeather | None:
    statement = select(DimWeather).join(
        DimSession, DimSession.weather_id == DimWeather.weather_id
    ).where(DimSession.session_id == session_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def list_laps_for_strategy(session: AsyncSession, session_id: uuid.UUID) -> list[Row[Any]]:
    """Every driver's laps in compound-relevant order — used by
    `app/services/race_service.py` to derive tyre stints from where the
    `compound` value changes between consecutive laps."""
    statement = (
        select(
            DimDriver.full_name.label("driver"),
            FctLap.lap_number,
            FctLap.compound,
        )
        .join(DimDriver, DimDriver.driver_id == FctLap.driver_id)
        .where(FctLap.session_id == session_id)
        .order_by(DimDriver.full_name, FctLap.lap_number)
    )
    result = await session.execute(statement)
    return list(result.all())


async def race_exists(session: AsyncSession, session_id: uuid.UUID) -> bool:
    statement = select(DimSession.session_id).where(
        DimSession.session_id == session_id, DimSession.session_type == _RACE_SESSION_TYPE
    )
    result = await session.execute(statement)
    return result.first() is not None
