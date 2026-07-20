"""Read-only Gold-layer queries backing `/drivers*` (docs/08_API_SPECIFICATION.md).

Same rules as `season_repository.py`: SQL only (selecting, joining,
filtering, pagination) — no ranking, no formatting, no cross-season
rollups (career totals are summed in `app/services/driver_service.py`,
since `mart_driver_summary` is already one small row per season, not a
big fact table worth pushing an aggregate query for).
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Row, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    DimConstructor,
    DimDriver,
    DimSeason,
    DimSession,
    FctLap,
    FctResult,
    MartDriverSummary,
)


async def list_drivers(
    session: AsyncSession,
    *,
    season: int | None,
    constructor_id: uuid.UUID | None,
    nationality: str | None,
    active: bool | None,
    sort: str,
    page: int,
    limit: int,
) -> tuple[list[Row[Any]], int]:
    """`sort` is one of `"full_name"` (default) or `"driver_number"` — validated
    by the caller (`app/services/driver_service.py`), not here.
    """
    statement = (
        select(
            DimDriver.driver_id,
            DimDriver.driver_number,
            DimDriver.full_name,
            DimDriver.abbreviation,
            DimDriver.nationality,
            DimDriver.date_of_birth,
            DimDriver.team_id,
            DimConstructor.team_name.label("team"),
            DimDriver.rookie_season,
            DimDriver.world_titles,
            DimDriver.active,
        )
        .outerjoin(DimConstructor, DimConstructor.constructor_id == DimDriver.team_id)
    )

    if season is not None:
        # Membership is checked via `fct_results` (every driver who was
        # classified in a session that season), not `fct_laps` — lap data
        # only exists for FastF1-sourced sessions, so a driver from a
        # Jolpica-only historical season would otherwise be missed entirely.
        statement = statement.where(
            DimDriver.driver_id.in_(
                select(FctResult.driver_id)
                .join(DimSession, DimSession.session_id == FctResult.session_id)
                .join(DimSeason, DimSeason.season_id == DimSession.season_id)
                .where(DimSeason.year == season)
            )
        )
    if constructor_id is not None:
        statement = statement.where(DimDriver.team_id == constructor_id)
    if nationality is not None:
        statement = statement.where(DimDriver.nationality == nationality)
    if active is not None:
        statement = statement.where(DimDriver.active == active)

    total = (
        await session.execute(select(func.count()).select_from(statement.subquery()))
    ).scalar_one()

    sort_column = DimDriver.driver_number if sort == "driver_number" else DimDriver.full_name
    statement = statement.order_by(sort_column).offset((page - 1) * limit).limit(limit)
    result = await session.execute(statement)
    return list(result.all()), total


async def get_driver_by_id(session: AsyncSession, driver_id: uuid.UUID) -> Row[Any] | None:
    statement = (
        select(
            DimDriver.driver_id,
            DimDriver.driver_number,
            DimDriver.full_name,
            DimDriver.abbreviation,
            DimDriver.nationality,
            DimDriver.date_of_birth,
            DimDriver.team_id,
            DimConstructor.team_name.label("team"),
            DimDriver.rookie_season,
            DimDriver.world_titles,
            DimDriver.active,
        )
        .outerjoin(DimConstructor, DimConstructor.constructor_id == DimDriver.team_id)
        .where(DimDriver.driver_id == driver_id)
    )
    result = await session.execute(statement)
    return result.first()


async def list_season_summaries_for_driver(
    session: AsyncSession, driver_id: uuid.UUID
) -> list[Row[Any]]:
    """Every `mart_driver_summary` row for this driver, oldest season first."""
    statement = (
        select(DimSeason.year.label("season"), MartDriverSummary)
        .join(DimSeason, DimSeason.season_id == MartDriverSummary.season_id)
        .where(MartDriverSummary.driver_id == driver_id)
        .order_by(DimSeason.year)
    )
    result = await session.execute(statement)
    return list(result.all())


async def list_laps_for_driver(
    session: AsyncSession,
    driver_id: uuid.UUID,
    *,
    season: int | None,
    round_number: int | None,
    session_type: str | None,
    compound: str | None,
) -> list[Row[Any]]:
    statement = (
        select(
            DimSeason.year.label("season"),
            DimSession.round_number.label("round"),
            DimSession.race_name.label("race_name"),
            DimSession.session_type.label("session_type"),
            FctLap.lap_number,
            FctLap.lap_time,
            FctLap.sector_1,
            FctLap.sector_2,
            FctLap.sector_3,
            FctLap.compound,
            FctLap.tyre_life,
            FctLap.position,
            FctLap.pit_in,
            FctLap.pit_out,
        )
        .join(DimSession, DimSession.session_id == FctLap.session_id)
        .join(DimSeason, DimSeason.season_id == DimSession.season_id)
        .where(FctLap.driver_id == driver_id)
    )
    if season is not None:
        statement = statement.where(DimSeason.year == season)
    if round_number is not None:
        statement = statement.where(DimSession.round_number == round_number)
    if session_type is not None:
        statement = statement.where(DimSession.session_type == session_type)
    if compound is not None:
        statement = statement.where(FctLap.compound == compound)

    statement = statement.order_by(DimSeason.year, DimSession.round_number, FctLap.lap_number)
    result = await session.execute(statement)
    return list(result.all())
