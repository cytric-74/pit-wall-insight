"""`/sessions*` (docs/08_API_SPECIFICATION.md — "Sessions")."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Request

from app.dependencies.database import AnalyticsDbSession
from app.schemas.common import SuccessResponse
from app.schemas.session import SessionLapEntry, SessionMetadata, SessionResultEntry
from app.services import session_service
from app.utils.responses import build_meta

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get(
    "/{session_id}", response_model=SuccessResponse[SessionMetadata], summary="Session metadata"
)
async def get_session(
    session_id: uuid.UUID, request: Request, db: AnalyticsDbSession
) -> SuccessResponse[SessionMetadata]:
    data = await session_service.get_session(db, session_id)
    return SuccessResponse(data=data, meta=build_meta(request))


@router.get(
    "/{session_id}/results",
    response_model=SuccessResponse[list[SessionResultEntry]],
    summary="Session results",
)
async def get_session_results(
    session_id: uuid.UUID, request: Request, db: AnalyticsDbSession
) -> SuccessResponse[list[SessionResultEntry]]:
    data = await session_service.get_results(db, session_id)
    return SuccessResponse(data=data, meta=build_meta(request))


@router.get(
    "/{session_id}/laps", response_model=SuccessResponse[list[SessionLapEntry]], summary="Lap table"
)
async def get_session_laps(
    session_id: uuid.UUID, request: Request, db: AnalyticsDbSession
) -> SuccessResponse[list[SessionLapEntry]]:
    data = await session_service.get_laps(db, session_id)
    return SuccessResponse(data=data, meta=build_meta(request))
