"""Response schemas for `/health`, `/ready`, and `/live`."""

from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"
    environment: str
    version: str


class ReadinessResponse(BaseModel):
    """`/ready` only checks the analytics/gold database — the only database
    the API layer actually serves traffic from (docs/06_DATA_ENGINEERING.md
    Decision 005, "API Reads Only Gold Models"); the raw/bronze database is
    ingestion's concern, not something a request being "ready" depends on.
    """

    status: str = "ready"


class LivenessResponse(BaseModel):
    """No dependency checks at all — a process that can answer HTTP requests
    is alive, whether or not any database is reachable (that's `/ready`'s
    job); conflating the two would make `/live` fail (and get the process
    restarted by an orchestrator) for a transient DB outage it didn't cause.
    """

    status: str = "alive"
