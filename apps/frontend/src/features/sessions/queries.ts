import type { RaceListItem } from "@pit-wall-insight/shared-types";
import { useQueries, useQuery } from "@tanstack/react-query";

import { getSession, getSessionLaps, getSessionResults } from "./api.js";

export const sessionKeys = {
  all: ["sessions"] as const,
  detail: (id: string) => [...sessionKeys.all, "detail", id] as const,
  results: (id: string) => [...sessionKeys.all, id, "results"] as const,
  laps: (id: string) => [...sessionKeys.all, id, "laps"] as const,
};

export function useSession(sessionId: string | undefined) {
  return useQuery({
    queryKey: sessionKeys.detail(sessionId ?? ""),
    queryFn: () => getSession(sessionId!),
    enabled: sessionId !== undefined,
  });
}

export function useSessionResults(sessionId: string | undefined) {
  return useQuery({
    queryKey: sessionKeys.results(sessionId ?? ""),
    queryFn: () => getSessionResults(sessionId!),
    enabled: sessionId !== undefined,
  });
}

export function useSessionLaps(sessionId: string | undefined) {
  return useQuery({
    queryKey: sessionKeys.laps(sessionId ?? ""),
    queryFn: () => getSessionLaps(sessionId!),
    enabled: sessionId !== undefined,
  });
}

/** One `GET /sessions/{id}/results` query per race, in the same order as
 * `races` — shared (by query key, `sessionKeys.results`) with
 * `useSessionResults` above, so a race already fetched individually isn't
 * re-fetched here, and vice versa. Used by Drivers (per-round position
 * history) and Constructors (season performance/driver comparison) to
 * reconstruct a season timeline from individual race results, since no
 * endpoint returns that directly. */
export function useSessionResultsForRaces(races: readonly RaceListItem[] | undefined) {
  return useQueries({
    queries: (races ?? []).map((race) => ({
      queryKey: sessionKeys.results(race.id),
      queryFn: () => getSessionResults(race.id),
    })),
  });
}
