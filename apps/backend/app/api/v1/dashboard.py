"""`/dashboard` and `/dashboard/highlights` (docs/08_API_SPECIFICATION.md).

Routers only parse the request, call a service, and wrap the result in the
standard envelope — no business logic (docs/05_BACKEND_ARCHITECTURE.md,
"Never execute SQL in routers" / "Never duplicate business logic").
"""

from __future__ import annotations

from datetime import UTC
from email.utils import format_datetime

from fastapi import APIRouter, Request, Response

from app.dependencies.database import AnalyticsDbSession
from app.schemas.common import SuccessResponse
from app.schemas.dashboard import DashboardData, DashboardHighlights
from app.services import dashboard_service
from app.utils.responses import build_meta

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=SuccessResponse[DashboardData], summary="Dashboard overview")
async def get_dashboard(
    request: Request, response: Response, db: AnalyticsDbSession
) -> SuccessResponse[DashboardData] | Response:
    """The most cacheable endpoint in the API — a completed season's
    standings only change when a new (offline, batch) ingestion run
    completes, so a conditional request answered with a bare `304` (no
    recompute, no re-serialization) is safe whenever `dim_season.updated_at`
    hasn't moved since the client's last fetch (Phase 7 audit, Medium).
    """
    last_modified = await dashboard_service.get_dashboard_last_modified(db)
    if last_modified is not None:
        # `dim_season.updated_at` is `DateTime(timezone=True)`, but SQLite
        # (used in this project's tests — no Postgres in this environment)
        # round-trips it as naive rather than tz-aware; assumed UTC here
        # like the rest of the app does (e.g. `app/utils/responses.py`'s
        # `datetime.now(UTC)`), since every audit-trail timestamp in this
        # warehouse is written in UTC regardless of what the driver reports.
        if last_modified.tzinfo is None:
            last_modified = last_modified.replace(tzinfo=UTC)
        etag = f'W/"{last_modified.timestamp()}"'
        if request.headers.get("if-none-match") == etag:
            return Response(status_code=304)
        response.headers["ETag"] = etag
        response.headers["Last-Modified"] = format_datetime(last_modified, usegmt=True)

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
