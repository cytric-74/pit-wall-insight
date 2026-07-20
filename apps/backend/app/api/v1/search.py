"""`/search` (docs/08_API_SPECIFICATION.md — "Search")."""

from __future__ import annotations

from fastapi import APIRouter, Query, Request

from app.dependencies.database import AnalyticsDbSession
from app.schemas.common import SuccessResponse
from app.schemas.search import SearchResults
from app.services import search_service
from app.utils.responses import build_meta

router = APIRouter(tags=["Search"])


@router.get("/search", response_model=SuccessResponse[SearchResults], summary="Global search")
async def search(
    request: Request,
    db: AnalyticsDbSession,
    query: str = Query(..., min_length=1),
) -> SuccessResponse[SearchResults]:
    data = await search_service.search(db, query)
    return SuccessResponse(data=data, meta=build_meta(request))
