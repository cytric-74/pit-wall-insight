"""Integration tests for `/api/v1/seasons*`."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tests.factories import seed_2024_two_race_season


async def test_list_seasons_returns_a_collection_response_with_pagination(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    response = await client.get("/api/v1/seasons")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"][0]["year"] == 2024
    assert body["pagination"] == {"page": 1, "limit": 25, "total": 1, "pages": 1}


async def test_get_season_summary_returns_the_requested_year(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    response = await client.get("/api/v1/seasons/2024")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["year"] == 2024
    assert body["data"]["championDriver"] == "Max Verstappen"
    assert body["data"]["championshipGap"] == 14.0


async def test_get_season_summary_returns_404_for_an_unknown_year(client: AsyncClient) -> None:
    response = await client.get("/api/v1/seasons/1999")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "NOT_FOUND"


async def test_get_standings_returns_ranked_driver_and_constructor_lists(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    response = await client.get("/api/v1/seasons/2024/standings")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["drivers"][0] == {
        "position": 1,
        "driver": "Max Verstappen",
        "team": "Red Bull Racing",
        "points": 50,
        "wins": 2,
    }
    assert body["data"]["constructors"][0]["constructor"] == "Red Bull Racing"


async def test_get_calendar_returns_rounds_in_order(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    response = await client.get("/api/v1/seasons/2024/calendar")

    assert response.status_code == 200
    body = response.json()
    assert [entry["raceName"] for entry in body["data"]] == [
        "Bahrain Grand Prix",
        "Saudi Arabian Grand Prix",
    ]
    assert body["data"][0]["circuit"] == "Bahrain International Circuit"
