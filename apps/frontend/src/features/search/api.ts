import type { SearchResults } from "@pit-wall-insight/shared-types";

import { apiGet } from "../../lib/api-client.js";

/**
 * `/search` (docs/08_API_SPECIFICATION.md — "Search"). No dedicated
 * Search page exists in the frontend yet — this formalizes the API
 * surface (types, fetch function, query hook), the same treatment given
 * to Sessions and Comparison.
 */
export function search(query: string): Promise<SearchResults> {
  return apiGet<SearchResults>("/search", { query });
}
