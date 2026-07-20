import type { DriverLap, RaceListItem, SessionResultEntry } from "@pit-wall-insight/shared-types";
import type { UseQueryResult } from "@tanstack/react-query";

export interface RoundPosition {
  round: number;
  grid: number | null;
  finish: number | null;
}

/** Reconstructs one driver's round-by-round grid/finish positions from the
 * per-race `GET /sessions/{id}/results` queries in `useSessionResultsForRaces`
 * — no single endpoint returns this directly (see `api.ts`). */
export function extractRoundPositions(
  races: readonly RaceListItem[],
  resultsQueries: readonly UseQueryResult<SessionResultEntry[]>[],
  driverName: string,
): RoundPosition[] {
  return races.map((race, index) => {
    const results = resultsQueries[index]?.data ?? [];
    const row = results.find((entry) => entry.driver === driverName);
    return {
      round: race.round,
      grid: row?.gridPosition ?? null,
      finish: row?.finishPosition ?? null,
    };
  });
}

export interface PaceSeries {
  categories: number[];
  driverData: number[];
  teammateData: number[] | undefined;
}

/** Aligns a driver's lap times with their teammate's for the same race —
 * only laps where *both* have a recorded time are kept, so the two series
 * stay the same length as the shared `categories` axis requires. Falls
 * back to the driver's own laps alone when there's no teammate data. */
export function buildPaceSeries(
  driverLaps: readonly DriverLap[],
  teammateLaps: readonly DriverLap[] | undefined,
): PaceSeries {
  const sortedDriverLaps = [...driverLaps]
    .filter((lap) => lap.lapTime != null)
    .sort((a, b) => a.lapNumber - b.lapNumber);

  if (!teammateLaps) {
    return {
      categories: sortedDriverLaps.map((lap) => lap.lapNumber),
      driverData: sortedDriverLaps.map((lap) => lap.lapTime!),
      teammateData: undefined,
    };
  }

  const teammateTimeByLap = new Map(
    teammateLaps.filter((lap) => lap.lapTime != null).map((lap) => [lap.lapNumber, lap.lapTime!]),
  );
  const shared = sortedDriverLaps.filter((lap) => teammateTimeByLap.has(lap.lapNumber));

  return {
    categories: shared.map((lap) => lap.lapNumber),
    driverData: shared.map((lap) => lap.lapTime!),
    teammateData: shared.map((lap) => teammateTimeByLap.get(lap.lapNumber)!),
  };
}
