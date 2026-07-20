import { MutationCache, QueryCache, QueryClient } from "@tanstack/react-query";

import { reportClientError } from "./error-boundary.js";

/**
 * One `QueryClient` for the whole app (created once, outside React, per
 * TanStack Query's own recommendation — never inside a component body,
 * which would recreate the cache on every render). `QueryCache`/
 * `MutationCache` `onError` give every failed fetch a single, guaranteed
 * logging point — before this, a failed query was invisible to both the
 * user (pages only ever checked `isPending`/`data`) and whoever operates
 * the app, since nothing observed it at all (Phase 7 audit, Critical).
 */
export const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: (error, query) => {
      reportClientError(error, { queryKey: query.queryKey });
    },
  }),
  mutationCache: new MutationCache({
    onError: (error, _variables, _context, mutation) => {
      reportClientError(error, { mutationKey: mutation.options.mutationKey });
    },
  }),
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
