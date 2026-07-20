"""Builds the `meta` block every `SuccessResponse`/`CollectionResponse` carries.

Kept out of individual routers so every endpoint stamps `meta` identically
(same request id, same execution-time calculation) rather than each one
reimplementing it slightly differently.
"""

from __future__ import annotations

import math
import time
from datetime import UTC, datetime

from starlette.requests import Request

from app.schemas.common import Meta, Pagination


def build_meta(request: Request) -> Meta:
    """Read `request.state.request_id`/`start_time` (set by
    `RequestContextMiddleware`) and turn them into a `Meta` instance.

    `execution_time` is formatted as `"<n>ms"` to match docs/08_API_SPECIFICATION.md's
    example envelope (`"execution_time": "42ms"`) literally, rather than a
    bare number.
    """
    start_time = getattr(request.state, "start_time", None)
    elapsed_ms = (time.perf_counter() - start_time) * 1000 if start_time is not None else 0.0
    return Meta(
        request_id=getattr(request.state, "request_id", None),
        execution_time=f"{elapsed_ms:.0f}ms",
        timestamp=datetime.now(UTC),
    )


def build_pagination(total: int, page: int, limit: int) -> Pagination:
    """Build the `Pagination` block for a collection response.

    Five routers each copy-pasted this exact `math.ceil(total / limit) if
    limit else 0` plus `Pagination(...)` construction (Phase 7 audit,
    Medium). The `if limit else 0` guard was always dead code — every
    router constrains `limit` with `Query(..., ge=1)`, so it can never be
    falsy — and is dropped here rather than carried over.
    """
    return Pagination(page=page, limit=limit, total=total, pages=math.ceil(total / limit))
