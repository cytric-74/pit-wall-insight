"""Cross-router tests for invalid pagination and malformed UUID path params.

`page=0`, `limit=101`, and non-UUID path segments all correctly 422 today
via FastAPI/Pydantic's own validation (`Query(..., ge=1)` etc.), but until
now nothing asserted it — a future refactor that accidentally loosened one
of those constraints wouldn't have been caught by anything (Phase 7 audit,
Low). Covers a couple of representative routers per the audit's own
suggested scope, not every endpoint that happens to share the pattern.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "path",
    ["/api/v1/drivers", "/api/v1/races", "/api/v1/constructors", "/api/v1/circuits"],
)
async def test_page_zero_is_rejected(path: str, client: AsyncClient) -> None:
    response = await client.get(path, params={"page": 0})

    assert response.status_code == 422


@pytest.mark.parametrize(
    "path",
    ["/api/v1/drivers", "/api/v1/races", "/api/v1/constructors", "/api/v1/circuits"],
)
async def test_limit_over_100_is_rejected(path: str, client: AsyncClient) -> None:
    response = await client.get(path, params={"limit": 101})

    assert response.status_code == 422


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/drivers/not-a-uuid",
        "/api/v1/races/not-a-uuid",
        "/api/v1/constructors/not-a-uuid",
        "/api/v1/circuits/not-a-uuid",
        "/api/v1/sessions/not-a-uuid",
    ],
)
async def test_malformed_uuid_path_param_is_rejected(path: str, client: AsyncClient) -> None:
    response = await client.get(path)

    assert response.status_code == 422
