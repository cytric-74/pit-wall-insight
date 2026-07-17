"""Unversioned infrastructure endpoint(s) — deployment health checks.

Kept outside `/api/{version}` since health checks are an infrastructure
concern, not a versioned business capability (see docs/05_BACKEND_ARCHITECTURE.md
and docs/11_DEPLOYMENT.md, "Health Endpoints").
"""

from __future__ import annotations

from fastapi import APIRouter

from app.dependencies.config import SettingsDep
from app.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse, summary="Application health check")
async def get_health(settings: SettingsDep) -> HealthResponse:
    return HealthResponse(environment=settings.environment.value, version=settings.api_version)
