"""Integration tests for `/api/v1/circuits*`."""

from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tests.factories import seed_2024_two_race_season, seed_driver_and_constructor_stats


async def test_list_circuits(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    response = await client.get("/api/v1/circuits")

    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total"] == 1
    assert body["data"][0]["name"] == "Bahrain International Circuit"


async def test_get_circuit_returns_404_for_an_unknown_id(client: AsyncClient) -> None:
    response = await client.get(f"/api/v1/circuits/{uuid.uuid4()}")

    assert response.status_code == 404


async def test_get_circuit_history_returns_only_races_at_that_circuit(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    response = await client.get(f"/api/v1/circuits/{seeded.circuit_id}/history")

    assert response.status_code == 200
    body = response.json()
    # Only Bahrain is linked to this circuit in the fixture -- Jeddah has circuit_id=None.
    assert len(body["data"]) == 1
    assert body["data"][0]["raceName"] == "Bahrain Grand Prix"
    assert body["data"][0]["winner"] == "Max Verstappen"


async def test_get_circuit_records_returns_the_fastest_lap_ever_recorded(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    response = await client.get(f"/api/v1/circuits/{seeded.circuit_id}/records")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["driver"] == "Max Verstappen"
    assert body["data"]["lapTime"] == 94.2
