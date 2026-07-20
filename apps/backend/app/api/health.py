"""Unversioned infrastructure endpoint(s) — deployment health checks.

Kept outside `/api/{version}` since health checks are an infrastructure
concern, not a versioned business capability (see docs/05_BACKEND_ARCHITECTURE.md
and docs/11_DEPLOYMENT.md, "Health Endpoints").
"""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from app.dependencies.config import SettingsDep
from app.dependencies.database import AnalyticsDbSession
from app.exceptions.base import AppException
from app.schemas.health import HealthResponse, LivenessResponse, ReadinessResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse, summary="Application health check")
async def get_health(settings: SettingsDep) -> HealthResponse:
    return HealthResponse(environment=settings.environment.value, version=settings.api_version)


@router.get("/ready", response_model=ReadinessResponse, summary="Readiness probe")
async def get_ready(db: AnalyticsDbSession) -> ReadinessResponse:
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        raise AppException(
            "Analytics database is not reachable.", code="NOT_READY", status_code=503
        ) from exc
    return ReadinessResponse()


@router.get("/live", response_model=LivenessResponse, summary="Liveness probe")
async def get_live() -> LivenessResponse:
    return LivenessResponse()
