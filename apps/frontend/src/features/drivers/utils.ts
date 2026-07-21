import type { DriverLap, RaceListItem, SessionResultEntry } from "@pit-wall-insight/shared-types";
import type { UseQueryResult } from "@tanstack/react-query";

import { alignSeriesByCategory } from "../../lib/chart-alignment.js";

export interface RoundPosition {
  round: number;
  grid: number | null;
  finish: number | null;
}

export interface RoundPositionWithFinish extends RoundPosition {
  finish: number;
}

export interface RoundPositionWithGridAndFinish extends RoundPositionWithFinish {
  grid: number;
}

/** Type predicate narrowing `finish` to `number` — pairs with `.filter()`
 * so downstream `.finish` reads never need a `!` assertion whose safety
 * depends on the filter and the read staying in sync by convention alone
 * (Phase 7 audit, Low). */
export function hasFinish(row: RoundPosition): row is RoundPositionWithFinish {
  return row.finish !== null;
}

/** Same as `hasFinish`, additionally narrowing `grid` to `number`. */
export function hasGridAndFinish(row: RoundPosition): row is RoundPositionWithGridAndFinish {
  return row.grid !== null && row.finish !== null;
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

  const timedTeammateLaps = teammateLaps.filter((lap) => lap.lapTime != null);
  if (sortedDriverLaps.length === 0 || timedTeammateLaps.length === 0) {
    // Both groups must be non-empty for `alignSeriesByCategory`'s
    // intersection to mean "laps both have a time for" — with only one
    // (or neither) group present it would otherwise vacuously return that
    // one group's own laps instead of the empty intersection this case
    // actually is.
    return { categories: [], driverData: [], teammateData: [] };
  }

  const aligned = alignSeriesByCategory(
    [
      ...sortedDriverLaps.map((lap) => ({
        group: "driver",
        lapNumber: lap.lapNumber,
        lapTime: lap.lapTime!,
      })),
      ...timedTeammateLaps.map((lap) => ({
        group: "teammate",
        lapNumber: lap.lapNumber,
        lapTime: lap.lapTime!,
      })),
    ],
    (lap) => lap.group,
    (lap) => lap.lapNumber,
    (lap) => lap.lapTime,
  );

  const driverSeries = aligned.series.find((series) => series.key === "driver");
  const teammateSeries = aligned.series.find((series) => series.key === "teammate");

  return {
    categories: aligned.categories,
    driverData: driverSeries?.data ?? [],
    teammateData: teammateSeries?.data ?? [],
  };
}
