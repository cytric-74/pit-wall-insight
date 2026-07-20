"""Unit tests for `app/services/compare_service.py`.

`compare_drivers`/`compare_constructors` are exercised directly in
`test_driver_service.py`/`test_constructor_service.py` (this module reuses
them from the router without any additional composition — see this
module's own docstring); only `compare_races` has logic that belongs here.
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.exceptions.base import NotFoundError
from app.services import compare_service
from tests.factories import seed_2024_two_race_season


async def test_compare_races_returns_both_summaries(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        comparison = await compare_service.compare_races(
            session, seeded.bahrain_session_id, seeded.jeddah_session_id
        )

    assert comparison.race_a.race_name == "Bahrain Grand Prix"
    assert comparison.race_b.race_name == "Saudi Arabian Grand Prix"


async def test_compare_races_raises_not_found_when_either_race_is_unknown(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        with pytest.raises(NotFoundError):
            await compare_service.compare_races(session, seeded.bahrain_session_id, uuid.uuid4())
