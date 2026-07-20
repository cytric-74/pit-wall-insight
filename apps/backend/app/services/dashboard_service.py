"""Business logic behind `/dashboard` and `/dashboard/highlights` (docs/08_API_SPECIFICATION.md).

Neither endpoint takes a season parameter (docs/08 doesn't define one for
either), so both scope themselves to `season_repository.get_latest_season`
— the most recent year loaded into the warehouse. That's a deliberate,
simple policy rather than anything more clever (e.g. "the season with an
in-progress race weekend"), since the warehouse has no concept of "now"
beyond which seasons have been ingested.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.base import NotFoundError
from app.repositories import season_repository
from app.schemas.dashboard import DashboardData, DashboardHighlights, RecentRace
from app.services.season_service import (
    get_ranked_constructor_standings,
    get_ranked_driver_standings,
)

_RECENT_RACES_LIMIT = 5


async def get_dashboard(session: AsyncSession) -> DashboardData:
    season = await season_repository.get_latest_season(session)
    if season is None:
        raise NotFoundError("No season data available yet.")

    dashboard = await season_repository.get_mart_dashboard(session, season.season_id)
    recent_rows = await season_repository.list_recent_completed_races(
        session, season.season_id, limit=_RECENT_RACES_LIMIT
    )

    return DashboardData(
        season=season.year,
        champion_driver=season.champion_driver,
        champion_constructor=season.champion_constructor,
        driver_standings=await get_ranked_driver_standings(session, season.season_id),
        constructor_standings=await get_ranked_constructor_standings(session, season.season_id),
        recent_races=[
            RecentRace(round=row.round, race_name=row.race_name, winner=row.winner, date=row.date)
            for row in recent_rows
        ],
        fastest_lap_driver=dashboard.fastest_lap_driver if dashboard else None,
        fastest_lap_time=dashboard.fastest_lap_time if dashboard else None,
        fastest_pitstop=dashboard.fastest_pitstop if dashboard else None,
        average_overtakes=dashboard.average_overtakes if dashboard else None,
        championship_gap=dashboard.championship_gap if dashboard else None,
    )


async def get_dashboard_highlights(session: AsyncSession) -> DashboardHighlights:
    season = await season_repository.get_latest_season(session)
    if season is None:
        raise NotFoundError("No season data available yet.")

    recent_rows = await season_repository.list_recent_completed_races(
        session, season.season_id, limit=1
    )
    if not recent_rows:
        raise NotFoundError("No completed races yet this season.")

    race = recent_rows[0]
    return DashboardHighlights(
        race_name=race.race_name,
        winner=race.winner,
        pole=race.pole,
        fastest_lap=race.fastest_lap,
        retirements=race.retirements,
        weather=race.weather,
    )
