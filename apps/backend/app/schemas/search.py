"""Response DTOs for `/search` (docs/08_API_SPECIFICATION.md — "Search")."""

from __future__ import annotations

from app.schemas.base import CamelModel


class SearchResultItem(CamelModel):
    id: str
    label: str


class SearchResults(CamelModel):
    drivers: list[SearchResultItem]
    constructors: list[SearchResultItem]
    circuits: list[SearchResultItem]
    races: list[SearchResultItem]
    seasons: list[SearchResultItem]
