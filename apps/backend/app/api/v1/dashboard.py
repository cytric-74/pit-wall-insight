"""`/dashboard` and `/dashboard/highlights` (docs/08_API_SPECIFICATION.md).

Routers only parse the request, call a service, and wrap the result in the
standard envelope — no business logic (docs/05_BACKEND_ARCHITECTURE.md,
"Never execute SQL in routers" / "Never duplicate business logic").
"""

from __future__ import annotations

from fastapi import APIRouter, Request

from app.dependencies.database import AnalyticsDbSession
from app.schemas.common import SuccessResponse
from app.schemas.dashboard import DashboardData, DashboardHighlights
from app.services import dashboard_service
from app.utils.responses import build_meta

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=SuccessResponse[DashboardData], summary="Dashboard overview")
async def get_dashboard(
    request: Request, db: AnalyticsDbSession
) -> SuccessResponse[DashboardData]:
    data = await dashboard_service.get_dashboard(db)
    return SuccessResponse(data=data, meta=build_meta(request))


@router.get(
    "/highlights",
    response_model=SuccessResponse[DashboardHighlights],
    summary="Most recent race's highlights",
)
async def get_dashboard_highlights(
    request: Request, db: AnalyticsDbSession
) -> SuccessResponse[DashboardHighlights]:
    data = await dashboard_service.get_dashboard_highlights(db)
    return SuccessResponse(data=data, meta=build_meta(request))
