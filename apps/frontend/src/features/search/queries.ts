import { useQuery } from "@tanstack/react-query";

import { search } from "./api.js";

export const searchKeys = {
  all: ["search"] as const,
  query: (query: string) => [...searchKeys.all, query] as const,
};

/** Only fires once `query` is non-empty (after trimming) — the backend
 * rejects an empty `query` with a 422 (`min_length=1`). */
export function useSearch(query: string) {
  const trimmed = query.trim();
  return useQuery({
    queryKey: searchKeys.query(trimmed),
    queryFn: () => search(trimmed),
    enabled: trimmed.length > 0,
  });
}
