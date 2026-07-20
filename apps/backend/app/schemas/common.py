"""Shared response envelope schemas (see docs/08_API_SPECIFICATION.md).

Two envelope shapes cover every non-error response in this API:

- `SuccessResponse[T]` — one resource (`{"success": true, "data": {...},
  "meta": {...}}`), used whenever an endpoint returns a single object (even
  if that object internally contains lists, like `StandingsData`).
- `CollectionResponse[T]` — a paginated list of resources (`{"success":
  true, "data": [...], "pagination": {...}}`), used for endpoints whose
  whole response *is* a list of independently-paginatable items (e.g.
  `/seasons`).

Both reconcile docs/05_BACKEND_ARCHITECTURE.md's envelope (which nests
`timestamp`/`request_id` at the top level) with docs/08's (which nests
`request_id`/`execution_time` under `meta`) by folding everything —
`request_id`, `execution_time`, and `timestamp` — into `Meta`.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from app.schemas.base import CamelModel

# PEP 695 generic syntax (`class Foo[T]`) is what `target-version = "py312"`
# would normally prefer (see `pyproject.toml`), but this environment's
# actual interpreter is 3.11 (no Python 3.12 available here) — mypy can't
# even parse that syntax under a 3.11 host interpreter, so `Generic`/`TypeVar`
# stays the deliberate, tool-compatible choice for these two classes.
T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[dict[str, Any]] | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
    request_id: str | None = None


class Meta(CamelModel):
    request_id: str | None
    execution_time: str
    timestamp: datetime


class Pagination(CamelModel):
    page: int
    limit: int
    total: int
    pages: int


class SuccessResponse(CamelModel, Generic[T]):  # noqa: UP046
    success: bool = True
    data: T
    meta: Meta


class CollectionResponse(CamelModel, Generic[T]):  # noqa: UP046
    success: bool = True
    data: list[T]
    pagination: Pagination
