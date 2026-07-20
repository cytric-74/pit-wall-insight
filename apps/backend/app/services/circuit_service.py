"""Business logic behind `/circuits*` (docs/08_API_SPECIFICATION.md — "Circuits")."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DimCircuit
from app.repositories import circuit_repository
from app.schemas.circuit import Circuit, CircuitRaceHistoryEntry, CircuitRecord
from app.services.common import get_or_404


def _circuit_from_model(model: DimCircuit) -> Circuit:
    return Circuit(
        id=model.circuit_id,
        name=model.name,
        country=model.country,
        city=model.city,
        latitude=model.latitude,
        longitude=model.longitude,
    )


async def _get_circuit_or_404(session: AsyncSession, circuit_id: uuid.UUID) -> Circuit:
    model = await get_or_404(
        circuit_repository.get_circuit_by_id(session, circuit_id), f"Circuit {circuit_id} not found."
    )
    return _circuit_from_model(model)


async def list_circuits(
    session: AsyncSession, *, page: int, limit: int
) -> tuple[list[Circuit], int]:
    models, total = await circuit_repository.list_circuits(session, page=page, limit=limit)
    return [_circuit_from_model(model) for model in models], total


async def get_circuit(session: AsyncSession, circuit_id: uuid.UUID) -> Circuit:
    return await _get_circuit_or_404(session, circuit_id)


async def get_race_history(
    session: AsyncSession, circuit_id: uuid.UUID
) -> list[CircuitRaceHistoryEntry]:
    await _get_circuit_or_404(session, circuit_id)
    rows = await circuit_repository.list_race_history(session, circuit_id)
    return [
        CircuitRaceHistoryEntry(
            season=row.season,
            round=row.round,
            race_name=row.race_name,
            winner=row.winner,
            pole=row.pole,
            fastest_lap=row.fastest_lap,
        )
        for row in rows
    ]


async def get_track_record(session: AsyncSession, circuit_id: uuid.UUID) -> CircuitRecord:
    await _get_circuit_or_404(session, circuit_id)
    row = await circuit_repository.get_track_record(session, circuit_id)
    if row is None:
        return CircuitRecord(driver=None, lap_time=None, season=None, round=None)
    return CircuitRecord(driver=row.driver, lap_time=row.lap_time, season=row.season, round=row.round)
