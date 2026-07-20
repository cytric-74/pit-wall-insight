import { QueryClient } from "@tanstack/react-query";

/**
 * One `QueryClient` for the whole app (created once, outside React, per
 * TanStack Query's own recommendation — never inside a component body,
 * which would recreate the cache on every render).
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // This is analytical/historical F1 data, not a live feed — it
      // changes only when a new ingestion + transform run completes, so
      // there is no reason to refetch on every window focus.
      refetchOnWindowFocus: false,
      staleTime: 60_000,
    },
  },
});
