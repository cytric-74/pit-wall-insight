"""Business logic behind `/seasons*` (docs/08_API_SPECIFICATION.md — "Seasons").

Owns everything `season_repository` deliberately doesn't: turning ordered
rows into ranked `DriverStandingEntry`/`ConstructorStandingEntry` lists
(position numbers are assigned here, from row order, not stored anywhere),
resolving a season year to a 404 when it doesn't exist, and assembling the
DTOs routers return. `app/services/dashboard_service.py` reuses the
standings functions here rather than duplicating them, since `/dashboard`
and `/seasons/{year}/standings` need the same shape for different scopes.
"""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.base import NotFoundError
from app.models import DimSeason
from app.repositories import season_repository
from app.schemas.season import (
    CalendarEntry,
    ConstructorStandingEntry,
    DriverStandingEntry,
    SeasonListItem,
    SeasonSummary,
    StandingsData,
)


async def _get_season_or_404(session: AsyncSession, year: int) -> DimSeason:
    season = await season_repository.get_season_by_year(session, year)
    if season is None:
        raise NotFoundError(f"Season {year} not found.")
    return season


async def get_ranked_driver_standings(
    session: AsyncSession, season_id: uuid.UUID
) -> list[DriverStandingEntry]:
    rows = await season_repository.get_driver_standings(session, season_id)
    return [
        DriverStandingEntry(
            position=position,
            driver=row.driver,
            team=row.team,
            points=row.points,
            wins=row.wins,
        )
        for position, row in enumerate(rows, start=1)
    ]


async def get_ranked_constructor_standings(
    session: AsyncSession, season_id: uuid.UUID
) -> list[ConstructorStandingEntry]:
    rows = await season_repository.get_constructor_standings(session, season_id)
    return [
        ConstructorStandingEntry(
            position=position, constructor=row.constructor, points=row.points, wins=row.wins
        )
        for position, row in enumerate(rows, start=1)
    ]


async def list_seasons(
    session: AsyncSession, *, page: int, limit: int
) -> tuple[list[SeasonListItem], int]:
    rows, total = await season_repository.list_seasons(session, page=page, limit=limit)
    items = [
        SeasonListItem(
            year=row.year,
            race_count=row.race_count,
            sprint_count=row.sprint_count,
            champion_driver=row.champion_driver,
            champion_constructor=row.champion_constructor,
        )
        for row in rows
    ]
    return items, total


async def get_season_summary(session: AsyncSession, year: int) -> SeasonSummary:
    season = await _get_season_or_404(session, year)
    dashboard = await season_repository.get_mart_dashboard(session, season.season_id)
    return SeasonSummary(
        year=season.year,
        race_count=season.race_count,
        sprint_count=season.sprint_count,
        champion_driver=season.champion_driver,
        champion_constructor=season.champion_constructor,
        fastest_lap_driver=dashboard.fastest_lap_driver if dashboard else None,
        fastest_lap_time=dashboard.fastest_lap_time if dashboard else None,
        fastest_pitstop=dashboard.fastest_pitstop if dashboard else None,
        average_overtakes=dashboard.average_overtakes if dashboard else None,
        championship_gap=dashboard.championship_gap if dashboard else None,
    )


async def get_standings(session: AsyncSession, year: int) -> StandingsData:
    season = await _get_season_or_404(session, year)
    return StandingsData(
        season=season.year,
        drivers=await get_ranked_driver_standings(session, season.season_id),
        constructors=await get_ranked_constructor_standings(session, season.season_id),
    )


async def get_calendar(session: AsyncSession, year: int) -> list[CalendarEntry]:
    season = await _get_season_or_404(session, year)
    rows = await season_repository.get_calendar(session, season.season_id)
    return [
        CalendarEntry(
            round=row.round,
            race_name=row.race_name,
            date=row.date,
            circuit=row.circuit,
            country=row.country,
        )
        for row in rows
    ]
