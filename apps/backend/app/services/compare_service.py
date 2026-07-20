"""Business logic behind `/compare/races` (docs/08_API_SPECIFICATION.md — "Comparison").

`/compare/drivers` and `/compare/constructors` reuse
`driver_service.compare_drivers`/`constructor_service.compare_constructors`
directly from the router — there's no additional composition needed for
those two, so no wrapper lives here for them.
"""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.compare import RaceComparison
from app.services import race_service


async def compare_races(
    session: AsyncSession, race_a_id: uuid.UUID, race_b_id: uuid.UUID
) -> RaceComparison:
    race_a = await race_service.get_race(session, race_a_id)
    race_b = await race_service.get_race(session, race_b_id)
    return RaceComparison(race_a=race_a, race_b=race_b)
