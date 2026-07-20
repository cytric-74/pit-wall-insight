"""Read-only Gold-layer queries backing `/dashboard*` and `/seasons*`.

Pure SQL — selecting, joining, grouping, ordering, and paginating only. No
derived business metrics live here (no standings *rank* numbers, no
formatting, no "which season is current" policy) — those belong to
`app/services/`, per docs/05_BACKEND_ARCHITECTURE.md ("Repositories never
compute statistics"). Aggregate SQL (`SUM`/`COUNT` for a season's points and
win totals) is still just a query, the same category of work as filtering
or pagination, so it lives here rather than being pulled row-by-row and
summed in Python.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Row, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    DimCircuit,
    DimConstructor,
    DimDriver,
    DimSeason,
    DimSession,
    FctResult,
    MartDashboard,
    MartRaceSummary,
)

_RACE_SESSION_TYPE = "R"


async def get_latest_season(session: AsyncSession) -> DimSeason | None:
    """The most recent season loaded into the warehouse — `/dashboard`'s implicit scope."""
    result = await session.execute(select(DimSeason).order_by(DimSeason.year.desc()).limit(1))
    return result.scalar_one_or_none()


async def get_season_by_year(session: AsyncSession, year: int) -> DimSeason | None:
    result = await session.execute(select(DimSeason).where(DimSeason.year == year))
    return result.scalar_one_or_none()


async def list_seasons(
    session: AsyncSession, *, page: int, limit: int
) -> tuple[list[DimSeason], int]:
    total = (await session.execute(select(func.count()).select_from(DimSeason))).scalar_one()
    result = await session.execute(
        select(DimSeason).order_by(DimSeason.year.desc()).offset((page - 1) * limit).limit(limit)
    )
    return list(result.scalars().all()), total


async def get_mart_dashboard(session: AsyncSession, season_id: uuid.UUID) -> MartDashboard | None:
    result = await session.execute(
        select(MartDashboard).where(MartDashboard.season_id == season_id)
    )
    return result.scalar_one_or_none()


async def get_driver_standings(session: AsyncSession, season_id: uuid.UUID) -> list[Row[Any]]:
    """Every driver's total race points/wins this season, highest points first."""
    statement = (
        select(
            DimDriver.full_name.label("driver"),
            DimConstructor.team_name.label("team"),
            func.coalesce(func.sum(FctResult.points), 0.0).label("points"),
            func.sum(case((FctResult.finish_position == 1, 1), else_=0)).label("wins"),
        )
        .join(FctResult, FctResult.driver_id == DimDriver.driver_id)
        .join(DimSession, DimSession.session_id == FctResult.session_id)
        .outerjoin(DimConstructor, DimConstructor.constructor_id == DimDriver.team_id)
        .where(DimSession.season_id == season_id, DimSession.session_type == _RACE_SESSION_TYPE)
        .group_by(DimDriver.driver_id, DimDriver.full_name, DimConstructor.team_name)
        .order_by(func.coalesce(func.sum(FctResult.points), 0.0).desc())
    )
    result = await session.execute(statement)
    return list(result.all())


async def get_constructor_standings(
    session: AsyncSession, season_id: uuid.UUID
) -> list[Row[Any]]:
    """Every constructor's total race points/wins this season (summed across its drivers)."""
    statement = (
        select(
            DimConstructor.team_name.label("constructor"),
            func.coalesce(func.sum(FctResult.points), 0.0).label("points"),
            func.sum(case((FctResult.finish_position == 1, 1), else_=0)).label("wins"),
        )
        .join(DimDriver, DimDriver.team_id == DimConstructor.constructor_id)
        .join(FctResult, FctResult.driver_id == DimDriver.driver_id)
        .join(DimSession, DimSession.session_id == FctResult.session_id)
        .where(DimSession.season_id == season_id, DimSession.session_type == _RACE_SESSION_TYPE)
        .group_by(DimConstructor.constructor_id, DimConstructor.team_name)
        .order_by(func.coalesce(func.sum(FctResult.points), 0.0).desc())
    )
    result = await session.execute(statement)
    return list(result.all())


async def get_calendar(session: AsyncSession, season_id: uuid.UUID) -> list[Row[Any]]:
    """This season's race weekends in round order, with circuit name/country attached."""
    statement = (
        select(
            DimSession.round_number.label("round"),
            DimSession.race_name.label("race_name"),
            DimSession.date.label("date"),
            DimCircuit.name.label("circuit"),
            DimCircuit.country.label("country"),
        )
        .outerjoin(DimCircuit, DimCircuit.circuit_id == DimSession.circuit_id)
        .where(DimSession.season_id == season_id, DimSession.session_type == _RACE_SESSION_TYPE)
        .order_by(DimSession.round_number)
    )
    result = await session.execute(statement)
    return list(result.all())


async def list_recent_completed_races(
    session: AsyncSession, season_id: uuid.UUID, *, limit: int
) -> list[Row[Any]]:
    """The `limit` most recent races (by round) this season that already have
    a `mart_race_summary` row — i.e. races the transform has actually
    processed, not every calendar entry (an inner join to `MartRaceSummary`
    is what excludes not-yet-transformed rounds).
    """
    statement = (
        select(
            DimSession.round_number.label("round"),
            DimSession.race_name.label("race_name"),
            DimSession.date.label("date"),
            MartRaceSummary.winner.label("winner"),
            MartRaceSummary.pole.label("pole"),
            MartRaceSummary.fastest_lap.label("fastest_lap"),
            MartRaceSummary.retirements.label("retirements"),
            MartRaceSummary.weather.label("weather"),
        )
        .join(MartRaceSummary, MartRaceSummary.session_id == DimSession.session_id)
        .where(DimSession.season_id == season_id, DimSession.session_type == _RACE_SESSION_TYPE)
        .order_by(DimSession.round_number.desc())
        .limit(limit)
    )
    result = await session.execute(statement)
    return list(result.all())
