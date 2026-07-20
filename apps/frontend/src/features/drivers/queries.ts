import type { RaceListItem } from "@pit-wall-insight/shared-types";
import { useQueries, useQuery } from "@tanstack/react-query";

import {
  getConstructorDrivers,
  getCurrentSeasonRaces,
  getDriver,
  getDriverLaps,
  getDriverStatistics,
  getSessionResults,
  listDrivers,
  type DriverLapsParams,
  type ListDriversParams,
} from "./api.js";

export const driverKeys = {
  all: ["drivers"] as const,
  list: (params?: ListDriversParams) => [...driverKeys.all, "list", params ?? {}] as const,
  detail: (id: string) => [...driverKeys.all, "detail", id] as const,
  statistics: (id: string) => [...driverKeys.all, "statistics", id] as const,
  laps: (id: string, params?: DriverLapsParams) =>
    [...driverKeys.all, "laps", id, params ?? {}] as const,
  teammates: (constructorId: string) => [...driverKeys.all, "teammates", constructorId] as const,
};

export function useDrivers(params?: ListDriversParams) {
  return useQuery({
    queryKey: driverKeys.list(params),
    queryFn: () => listDrivers(params),
  });
}

export function useDriver(driverId: string | undefined) {
  return useQuery({
    queryKey: driverKeys.detail(driverId ?? ""),
    queryFn: () => getDriver(driverId!),
    enabled: driverId !== undefined,
  });
}

export function useDriverStatistics(driverId: string | undefined) {
  return useQuery({
    queryKey: driverKeys.statistics(driverId ?? ""),
    queryFn: () => getDriverStatistics(driverId!),
    enabled: driverId !== undefined,
  });
}

export function useDriverLaps(driverId: string | undefined, params?: DriverLapsParams) {
  return useQuery({
    queryKey: driverKeys.laps(driverId ?? "", params),
    queryFn: () => getDriverLaps(driverId!, params),
    enabled: driverId !== undefined,
  });
}

/** The other active driver at `constructorId`, if any — used as the
 * "teammate" for head-to-head comparisons on the Driver Dossier page. */
export function useTeammate(
  constructorId: string | undefined,
  excludeDriverId: string | undefined,
) {
  const query = useQuery({
    queryKey: driverKeys.teammates(constructorId ?? ""),
    queryFn: () => getConstructorDrivers(constructorId!),
    enabled: constructorId !== undefined,
  });
  const teammate = query.data?.find((driver) => driver.id !== excludeDriverId);
  return { ...query, teammate };
}

export function useCurrentSeasonRaces() {
  return useQuery({
    queryKey: ["races", "current-season"] as const,
    queryFn: getCurrentSeasonRaces,
  });
}

/** One `GET /sessions/{id}/results` query per race, in the same order as
 * `races` — shared (by query key) between whichever components need
 * per-round results for more than one driver, so the underlying fetch
 * only happens once per race regardless of how many drivers read it. */
export function useSessionResultsForRaces(races: readonly RaceListItem[] | undefined) {
  return useQueries({
    queries: (races ?? []).map((race) => ({
      queryKey: ["sessions", race.id, "results"] as const,
      queryFn: () => getSessionResults(race.id),
    })),
  });
}
