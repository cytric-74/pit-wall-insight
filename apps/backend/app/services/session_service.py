"""Business logic behind `/sessions*` (docs/08_API_SPECIFICATION.md — "Sessions")."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.base import NotFoundError
from app.repositories import session_repository
from app.schemas.session import SessionLapEntry, SessionMetadata, SessionResultEntry


async def get_session(session: AsyncSession, session_id: uuid.UUID) -> SessionMetadata:
    row = await session_repository.get_session_by_id(session, session_id)
    if row is None:
        raise NotFoundError(f"Session {session_id} not found.")
    return SessionMetadata(
        id=row.session_id,
        season=row.season,
        round=row.round,
        race_name=row.race_name,
        session_type=row.session_type,
        circuit=row.circuit,
        date=row.date,
    )


async def _ensure_session_exists(session: AsyncSession, session_id: uuid.UUID) -> None:
    if not await session_repository.session_exists(session, session_id):
        raise NotFoundError(f"Session {session_id} not found.")


async def get_results(session: AsyncSession, session_id: uuid.UUID) -> list[SessionResultEntry]:
    await _ensure_session_exists(session, session_id)
    rows = await session_repository.list_results(session, session_id)
    return [
        SessionResultEntry(
            driver=row.driver,
            team=row.team,
            grid_position=row.grid_position,
            finish_position=row.finish_position,
            points=row.points,
            status=row.status,
            fastest_lap=row.fastest_lap,
            laps_completed=row.laps_completed,
        )
        for row in rows
    ]


async def get_laps(session: AsyncSession, session_id: uuid.UUID) -> list[SessionLapEntry]:
    await _ensure_session_exists(session, session_id)
    rows = await session_repository.list_laps(session, session_id)
    return [
        SessionLapEntry(
            driver=row.driver,
            lap_number=row.lap_number,
            lap_time=row.lap_time,
            compound=row.compound,
            tyre_life=row.tyre_life,
            position=row.position,
            pit_in=row.pit_in,
            pit_out=row.pit_out,
        )
        for row in rows
    ]
