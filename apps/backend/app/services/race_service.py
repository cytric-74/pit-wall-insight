"""Business logic behind `/races*` (docs/08_API_SPECIFICATION.md — "Races")."""

from __future__ import annotations

import itertools
import uuid
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import race_repository
from app.schemas.race import (
    DriverStrategy,
    PitstopEntry,
    PositionEntry,
    RaceListItem,
    RaceSummary,
    RaceWeather,
    TyreStint,
)
from app.services.common import ensure_or_404, get_or_404


async def _ensure_race_exists(session: AsyncSession, session_id: uuid.UUID) -> None:
    await ensure_or_404(race_repository.race_exists(session, session_id), f"Race {session_id} not found.")


async def list_races(
    session: AsyncSession, *, season: int | None, country: str | None, page: int, limit: int
) -> tuple[list[RaceListItem], int]:
    rows, total = await race_repository.list_races(
        session, season=season, country=country, page=page, limit=limit
    )
    items = [
        RaceListItem(
            id=row.session_id,
            season=row.season,
            round=row.round,
            race_name=row.race_name,
            circuit=row.circuit,
            country=row.country,
            date=row.date,
            winner=row.winner,
        )
        for row in rows
    ]
    return items, total


async def get_race(session: AsyncSession, session_id: uuid.UUID) -> RaceSummary:
    row = await get_or_404(
        race_repository.get_race_by_id(session, session_id), f"Race {session_id} not found."
    )
    return RaceSummary(
        id=row.session_id,
        season=row.season,
        round=row.round,
        race_name=row.race_name,
        circuit=row.circuit,
        country=row.country,
        date=row.date,
        winner=row.winner,
        pole=row.pole,
        fastest_lap=row.fastest_lap,
        retirements=row.retirements,
        weather=row.weather,
        average_pitstop=row.average_pitstop,
    )


async def get_positions(session: AsyncSession, session_id: uuid.UUID) -> list[PositionEntry]:
    await _ensure_race_exists(session, session_id)
    rows = await race_repository.list_positions(session, session_id)
    return [
        PositionEntry(driver=row.driver, lap_number=row.lap_number, position=row.position)
        for row in rows
    ]


async def get_pitstops(session: AsyncSession, session_id: uuid.UUID) -> list[PitstopEntry]:
    await _ensure_race_exists(session, session_id)
    rows = await race_repository.list_pitstops(session, session_id)
    return [
        PitstopEntry(
            driver=row.driver,
            lap=row.lap,
            pit_duration=row.pit_duration,
            stop_number=row.stop_number,
            compound_before=row.compound_before,
            compound_after=row.compound_after,
        )
        for row in rows
    ]


async def get_weather(session: AsyncSession, session_id: uuid.UUID) -> RaceWeather:
    await _ensure_race_exists(session, session_id)
    weather = await race_repository.get_weather(session, session_id)
    if weather is None:
        return RaceWeather(
            air_temperature=None,
            track_temperature=None,
            humidity=None,
            wind_speed=None,
            wind_direction=None,
            rainfall=None,
            pressure=None,
        )
    return RaceWeather(
        air_temperature=weather.air_temperature,
        track_temperature=weather.track_temperature,
        humidity=weather.humidity,
        wind_speed=weather.wind_speed,
        wind_direction=weather.wind_direction,
        rainfall=weather.rainfall,
        pressure=weather.pressure,
    )


async def get_strategy(session: AsyncSession, session_id: uuid.UUID) -> list[DriverStrategy]:
    """Tyre stints per driver, derived from where `compound` changes across
    consecutive laps — see `app/schemas/race.py` for why this doesn't use
    `fct_pitstop` (which is currently under-populated, a documented Phase 4
    gap).
    """
    await _ensure_race_exists(session, session_id)
    rows = await race_repository.list_laps_for_strategy(session, session_id)

    laps_by_driver: dict[str, list[tuple[float, str | None]]] = defaultdict(list)
    for row in rows:
        laps_by_driver[row.driver].append((row.lap_number, row.compound))

    strategies = []
    for driver, laps in laps_by_driver.items():
        stints: list[TyreStint] = []
        for compound, group in itertools.groupby(laps, key=lambda lap: lap[1]):
            group_laps = [lap_number for lap_number, _ in group]
            stints.append(
                TyreStint(
                    compound=compound,
                    start_lap=group_laps[0],
                    end_lap=group_laps[-1],
                    lap_count=len(group_laps),
                )
            )
        strategies.append(DriverStrategy(driver=driver, stints=stints))
    return strategies
