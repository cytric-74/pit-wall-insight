import type {
  ConstructorSeasonSummary,
  RaceListItem,
  SessionResultEntry,
} from "@pit-wall-insight/shared-types";
import type { UseQueryResult } from "@tanstack/react-query";

export interface ConstructorSeasonSummaryWithPitstopAverage extends ConstructorSeasonSummary {
  pitstopAverage: number;
}

/** Type predicate narrowing `pitstopAverage` to `number` — pairs with
 * `.filter()` so a downstream `.pitstopAverage` read never needs a `!`
 * assertion whose safety depends on the filter and the read staying in
 * sync by convention alone (Phase 7 audit, Low). */
export function hasPitstopAverage(
  entry: ConstructorSeasonSummary,
): entry is ConstructorSeasonSummaryWithPitstopAverage {
  return entry.pitstopAverage !== null;
}

/** This team's combined points per round, reconstructed from the per-race
 * `GET /sessions/{id}/results` queries — no endpoint returns a
 * constructor's round-by-round points directly. */
export function extractTeamPointsByRound(
  races: readonly RaceListItem[],
  resultsQueries: readonly UseQueryResult<SessionResultEntry[]>[],
  driverNames: readonly string[],
): number[] {
  return races.map((_, index) => {
    const results = resultsQueries[index]?.data ?? [];
    return results
      .filter((entry) => driverNames.includes(entry.driver))
      .reduce((sum, entry) => sum + (entry.points ?? 0), 0);
  });
}

export function cumulativeSum(values: readonly number[]): number[] {
  let total = 0;
  return values.map((value) => {
    total += value;
    return total;
  });
}

export interface DriverRoundPoints {
  driver: string;
  points: number[];
}

/** Each of this team's current drivers' points per round, for the "Driver
 * comparison" chart — same underlying per-race results as
 * `extractTeamPointsByRound`, split by driver instead of summed. */
export function extractDriverPointsByRound(
  races: readonly RaceListItem[],
  resultsQueries: readonly UseQueryResult<SessionResultEntry[]>[],
  driverNames: readonly string[],
): DriverRoundPoints[] {
  return driverNames.map((name) => ({
    driver: name,
    points: races.map((_, index) => {
      const results = resultsQueries[index]?.data ?? [];
      const row = results.find((entry) => entry.driver === name);
      return row?.points ?? 0;
    }),
  }));
}
