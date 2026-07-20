"""Shared Gold-layer test data for Phase 5 (dashboard/seasons/drivers/
constructors) tests.

Not a test file itself (no `test_` functions) — a helper seeding a small,
consistent two-driver/two-constructor/two-race 2024 season, reused by the
repository, service, and API-integration test files so they all assert
against the same known numbers rather than each hand-rolling similar rows.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models import (
    DimCircuit,
    DimConstructor,
    DimDriver,
    DimSeason,
    DimSession,
    FctLap,
    FctResult,
    MartConstructorSummary,
    MartDashboard,
    MartDriverSummary,
    MartRaceSummary,
)

_SOURCE = "test"
_PIPELINE_VERSION = "0.1.0"


@dataclass(frozen=True, slots=True)
class SeededSeason:
    season_id: uuid.UUID
    verstappen_id: uuid.UUID
    leclerc_id: uuid.UUID
    red_bull_id: uuid.UUID
    ferrari_id: uuid.UUID
    bahrain_session_id: uuid.UUID
    jeddah_session_id: uuid.UUID


async def seed_2024_two_race_season(
    session_factory: async_sessionmaker[AsyncSession],
) -> SeededSeason:
    """Verstappen (Red Bull) wins both rounds, Leclerc (Ferrari) is
    runner-up both times — Verstappen: 50 pts/2 wins, Leclerc: 36 pts/0
    wins, Red Bull: 50 pts/2 wins, Ferrari: 36 pts/0 wins. Round 2
    (Saudi Arabia) is the most recently-run race (higher round number).
    """
    season_id = uuid.uuid4()
    red_bull_id = uuid.uuid4()
    ferrari_id = uuid.uuid4()
    verstappen_id = uuid.uuid4()
    leclerc_id = uuid.uuid4()
    circuit_id = uuid.uuid4()
    bahrain_session_id = uuid.uuid4()
    jeddah_session_id = uuid.uuid4()

    async with session_factory() as session:
        session.add(
            DimSeason(
                season_id=season_id,
                source=_SOURCE,
                pipeline_version=_PIPELINE_VERSION,
                year=2024,
                race_count=2,
                sprint_count=0,
                champion_driver="Max Verstappen",
                champion_constructor="Red Bull Racing",
            )
        )
        # SQLAlchemy only auto-orders flush inserts across tables via
        # declared `relationship()`s, which these Gold models deliberately
        # don't have (see each model's docstring) — so dependency tiers are
        # flushed explicitly here, in FK order, rather than relying on
        # implicit ordering that only exists when relationships are declared.
        await session.flush()

        session.add(
            DimCircuit(
                circuit_id=circuit_id,
                source=_SOURCE,
                pipeline_version=_PIPELINE_VERSION,
                name="Bahrain International Circuit",
                country="Bahrain",
            )
        )
        session.add_all(
            [
                DimConstructor(
                    constructor_id=red_bull_id,
                    source=_SOURCE,
                    pipeline_version=_PIPELINE_VERSION,
                    team_name="Red Bull Racing",
                    active=True,
                ),
                DimConstructor(
                    constructor_id=ferrari_id,
                    source=_SOURCE,
                    pipeline_version=_PIPELINE_VERSION,
                    team_name="Ferrari",
                    active=True,
                ),
            ]
        )
        await session.flush()  # circuit/constructors before drivers depend on them

        session.add_all(
            [
                DimDriver(
                    driver_id=verstappen_id,
                    source=_SOURCE,
                    pipeline_version=_PIPELINE_VERSION,
                    full_name="Max Verstappen",
                    abbreviation="VER",
                    team_id=red_bull_id,
                    active=True,
                ),
                DimDriver(
                    driver_id=leclerc_id,
                    source=_SOURCE,
                    pipeline_version=_PIPELINE_VERSION,
                    full_name="Charles Leclerc",
                    abbreviation="LEC",
                    team_id=ferrari_id,
                    active=True,
                ),
            ]
        )
        await session.flush()  # drivers before sessions/results reference them

        session.add_all(
            [
                DimSession(
                    session_id=bahrain_session_id,
                    source=_SOURCE,
                    pipeline_version=_PIPELINE_VERSION,
                    season_id=season_id,
                    round_number=1,
                    race_name="Bahrain Grand Prix",
                    session_type="R",
                    date="2024-03-02",
                    circuit_id=circuit_id,
                ),
                DimSession(
                    session_id=jeddah_session_id,
                    source=_SOURCE,
                    pipeline_version=_PIPELINE_VERSION,
                    season_id=season_id,
                    round_number=2,
                    race_name="Saudi Arabian Grand Prix",
                    session_type="R",
                    date="2024-03-09",
                    circuit_id=None,
                ),
            ]
        )
        await session.flush()  # sessions before results/mart_race_summary reference them

        session.add_all(
            [
                FctResult(
                    result_id=uuid.uuid4(),
                    source=_SOURCE,
                    pipeline_version=_PIPELINE_VERSION,
                    driver_id=verstappen_id,
                    session_id=bahrain_session_id,
                    finish_position=1,
                    grid_position=1,
                    points=25,
                    status="Finished",
                ),
                FctResult(
                    result_id=uuid.uuid4(),
                    source=_SOURCE,
                    pipeline_version=_PIPELINE_VERSION,
                    driver_id=leclerc_id,
                    session_id=bahrain_session_id,
                    finish_position=2,
                    grid_position=2,
                    points=18,
                    status="Finished",
                ),
                FctResult(
                    result_id=uuid.uuid4(),
                    source=_SOURCE,
                    pipeline_version=_PIPELINE_VERSION,
                    driver_id=verstappen_id,
                    session_id=jeddah_session_id,
                    finish_position=1,
                    grid_position=1,
                    points=25,
                    status="Finished",
                ),
                FctResult(
                    result_id=uuid.uuid4(),
                    source=_SOURCE,
                    pipeline_version=_PIPELINE_VERSION,
                    driver_id=leclerc_id,
                    session_id=jeddah_session_id,
                    finish_position=2,
                    grid_position=2,
                    points=18,
                    status="Finished",
                ),
            ]
        )
        session.add(
            MartDashboard(
                season_id=season_id,
                source=_SOURCE,
                pipeline_version=_PIPELINE_VERSION,
                season=2024,
                drivers=2,
                constructors=2,
                races=2,
                fastest_pitstop=22.3,
                average_overtakes=2.0,
                fastest_lap_time=91.0,
                fastest_lap_driver="Max Verstappen",
                championship_gap=14.0,
            )
        )
        session.add_all(
            [
                MartRaceSummary(
                    session_id=bahrain_session_id,
                    source=_SOURCE,
                    pipeline_version=_PIPELINE_VERSION,
                    race="Bahrain Grand Prix",
                    winner="Max Verstappen",
                    pole="Max Verstappen",
                    fastest_lap="Max Verstappen",
                    average_pitstop=None,
                    weather="Dry",
                    retirements=0,
                ),
                MartRaceSummary(
                    session_id=jeddah_session_id,
                    source=_SOURCE,
                    pipeline_version=_PIPELINE_VERSION,
                    race="Saudi Arabian Grand Prix",
                    winner="Max Verstappen",
                    pole="Charles Leclerc",
                    fastest_lap="Charles Leclerc",
                    average_pitstop=None,
                    weather="Dry",
                    retirements=2,
                ),
            ]
        )
        await session.commit()

    return SeededSeason(
        season_id=season_id,
        verstappen_id=verstappen_id,
        leclerc_id=leclerc_id,
        red_bull_id=red_bull_id,
        ferrari_id=ferrari_id,
        bahrain_session_id=bahrain_session_id,
        jeddah_session_id=jeddah_session_id,
    )


async def seed_driver_and_constructor_stats(
    session_factory: async_sessionmaker[AsyncSession], seeded: SeededSeason
) -> None:
    """Adds `fct_laps` (for Verstappen's Bahrain race) and the 2024
    `mart_driver_summary`/`mart_constructor_summary` rows on top of a
    season already seeded by `seed_2024_two_race_season` — needed for the
    Phase 5b (drivers/constructors) tests, which `seed_2024_two_race_season`
    alone doesn't provide.
    """
    async with session_factory() as session:
        session.add_all(
            [
                FctLap(
                    lap_id=uuid.uuid4(),
                    source=_SOURCE,
                    pipeline_version=_PIPELINE_VERSION,
                    driver_id=seeded.verstappen_id,
                    session_id=seeded.bahrain_session_id,
                    lap_number=1,
                    lap_time=95.0,
                    compound="SOFT",
                    position=1,
                    pit_in=False,
                    pit_out=False,
                ),
                FctLap(
                    lap_id=uuid.uuid4(),
                    source=_SOURCE,
                    pipeline_version=_PIPELINE_VERSION,
                    driver_id=seeded.verstappen_id,
                    session_id=seeded.bahrain_session_id,
                    lap_number=2,
                    lap_time=94.5,
                    compound="HARD",
                    position=1,
                    pit_in=False,
                    pit_out=False,
                ),
            ]
        )
        session.add_all(
            [
                MartDriverSummary(
                    mart_driver_summary_id=uuid.uuid4(),
                    source=_SOURCE,
                    pipeline_version=_PIPELINE_VERSION,
                    season_id=seeded.season_id,
                    driver_id=seeded.verstappen_id,
                    driver="Max Verstappen",
                    wins=2,
                    podiums=2,
                    poles=2,
                    fastest_laps=1,
                    average_finish=1.0,
                    average_qualifying=1.0,
                    consistency_score=100.0,
                    pit_efficiency=22.3,
                    race_pace=94.7,
                    qualifying_pace=90.0,
                ),
                MartDriverSummary(
                    mart_driver_summary_id=uuid.uuid4(),
                    source=_SOURCE,
                    pipeline_version=_PIPELINE_VERSION,
                    season_id=seeded.season_id,
                    driver_id=seeded.leclerc_id,
                    driver="Charles Leclerc",
                    wins=0,
                    podiums=2,
                    poles=0,
                    fastest_laps=1,
                    average_finish=2.0,
                    average_qualifying=2.0,
                    consistency_score=95.0,
                    pit_efficiency=24.0,
                    race_pace=95.5,
                    qualifying_pace=91.0,
                ),
            ]
        )
        session.add_all(
            [
                MartConstructorSummary(
                    mart_constructor_summary_id=uuid.uuid4(),
                    source=_SOURCE,
                    pipeline_version=_PIPELINE_VERSION,
                    season_id=seeded.season_id,
                    constructor_id=seeded.red_bull_id,
                    constructor="Red Bull Racing",
                    wins=2,
                    podiums=2,
                    pitstop_average=22.3,
                    average_points=25.0,
                    dnf_rate=0.0,
                ),
                MartConstructorSummary(
                    mart_constructor_summary_id=uuid.uuid4(),
                    source=_SOURCE,
                    pipeline_version=_PIPELINE_VERSION,
                    season_id=seeded.season_id,
                    constructor_id=seeded.ferrari_id,
                    constructor="Ferrari",
                    wins=0,
                    podiums=2,
                    pitstop_average=24.0,
                    average_points=18.0,
                    dnf_rate=0.0,
                ),
            ]
        )
        await session.commit()


async def seed_2023_season_for_verstappen(
    session_factory: async_sessionmaker[AsyncSession], verstappen_id: uuid.UUID
) -> None:
    """A second, earlier season with just one `mart_driver_summary` row for
    Verstappen — needed to test career-wide rollups spanning more than one
    season loaded into the warehouse.
    """
    season_id = uuid.uuid4()
    async with session_factory() as session:
        session.add(
            DimSeason(
                season_id=season_id,
                source=_SOURCE,
                pipeline_version=_PIPELINE_VERSION,
                year=2023,
                race_count=1,
                champion_driver="Max Verstappen",
                champion_constructor="Red Bull Racing",
            )
        )
        await session.flush()
        session.add(
            MartDriverSummary(
                mart_driver_summary_id=uuid.uuid4(),
                source=_SOURCE,
                pipeline_version=_PIPELINE_VERSION,
                season_id=season_id,
                driver_id=verstappen_id,
                driver="Max Verstappen",
                wins=1,
                podiums=1,
                poles=1,
                fastest_laps=1,
                average_finish=1.0,
                average_qualifying=1.0,
                consistency_score=100.0,
                pit_efficiency=20.0,
                race_pace=93.0,
                qualifying_pace=89.0,
            )
        )
        await session.commit()
