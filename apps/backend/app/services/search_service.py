"""Business logic behind `/search` (docs/08_API_SPECIFICATION.md — "Search")."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import search_repository
from app.schemas.search import SearchResultItem, SearchResults


async def search(session: AsyncSession, query: str) -> SearchResults:
    drivers = await search_repository.search_drivers(session, query)
    constructors = await search_repository.search_constructors(session, query)
    circuits = await search_repository.search_circuits(session, query)
    races = await search_repository.search_races(session, query)
    seasons = await search_repository.search_seasons(session, query)

    return SearchResults(
        drivers=[
            SearchResultItem(id=str(driver.driver_id), label=driver.full_name)
            for driver in drivers
        ],
        constructors=[
            SearchResultItem(id=str(constructor.constructor_id), label=constructor.team_name)
            for constructor in constructors
        ],
        circuits=[
            SearchResultItem(id=str(circuit.circuit_id), label=circuit.name)
            for circuit in circuits
        ],
        races=[
            SearchResultItem(id=str(row.session_id), label=f"{row.race_name} ({row.year})")
            for row in races
        ],
        seasons=[
            SearchResultItem(id=str(season_row.year), label=str(season_row.year))
            for season_row in seasons
        ],
    )
