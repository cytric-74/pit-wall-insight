"""`/circuits*` (docs/08_API_SPECIFICATION.md — "Circuits")."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query, Request

from app.dependencies.database import AnalyticsDbSession
from app.schemas.circuit import Circuit, CircuitRaceHistoryEntry, CircuitRecord
from app.schemas.common import CollectionResponse, SuccessResponse
from app.services import circuit_service
from app.utils.responses import build_meta, build_pagination

router = APIRouter(prefix="/circuits", tags=["Circuits"])


@router.get("", response_model=CollectionResponse[Circuit], summary="Circuit list")
async def list_circuits(
    db: AnalyticsDbSession,
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
) -> CollectionResponse[Circuit]:
    items, total = await circuit_service.list_circuits(db, page=page, limit=limit)
    return CollectionResponse(data=items, pagination=build_pagination(total, page, limit))


@router.get("/{circuit_id}", response_model=SuccessResponse[Circuit], summary="Circuit details")
async def get_circuit(
    circuit_id: uuid.UUID, request: Request, db: AnalyticsDbSession
) -> SuccessResponse[Circuit]:
    data = await circuit_service.get_circuit(db, circuit_id)
    return SuccessResponse(data=data, meta=build_meta(request))


@router.get(
    "/{circuit_id}/history",
    response_model=SuccessResponse[list[CircuitRaceHistoryEntry]],
    summary="Historical results",
)
async def get_circuit_history(
    circuit_id: uuid.UUID, request: Request, db: AnalyticsDbSession
) -> SuccessResponse[list[CircuitRaceHistoryEntry]]:
    data = await circuit_service.get_race_history(db, circuit_id)
    return SuccessResponse(data=data, meta=build_meta(request))


@router.get(
    "/{circuit_id}/records", response_model=SuccessResponse[CircuitRecord], summary="Track records"
)
async def get_circuit_records(
    circuit_id: uuid.UUID, request: Request, db: AnalyticsDbSession
) -> SuccessResponse[CircuitRecord]:
    data = await circuit_service.get_track_record(db, circuit_id)
    return SuccessResponse(data=data, meta=build_meta(request))
