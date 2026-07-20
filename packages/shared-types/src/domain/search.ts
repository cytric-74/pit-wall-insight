/**
 * `/search` (docs/08_API_SPECIFICATION.md — "Search"). Mirrors
 * `apps/backend/app/schemas/search.py` exactly.
 */

export interface SearchResultItem {
  id: string;
  label: string;
}

export interface SearchResults {
  drivers: SearchResultItem[];
  constructors: SearchResultItem[];
  circuits: SearchResultItem[];
  races: SearchResultItem[];
  seasons: SearchResultItem[];
}
