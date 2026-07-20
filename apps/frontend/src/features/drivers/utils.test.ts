import type { DriverLap, RaceListItem, SessionResultEntry } from "@pit-wall-insight/shared-types";
import type { UseQueryResult } from "@tanstack/react-query";
import { describe, expect, it } from "vitest";

import { buildPaceSeries, extractRoundPositions } from "./utils.js";
import type { RoundPosition } from "./utils.js";

function lap(lapNumber: number, lapTime: number | null): DriverLap {
  return {
    season: 2024,
    round: 1,
    raceName: null,
    sessionType: "R",
    lapNumber,
    lapTime,
    sector1: null,
    sector2: null,
    sector3: null,
    compound: null,
    tyreLife: null,
    position: null,
    pitIn: null,
    pitOut: null,
  };
}

function race(round: number, name: string): RaceListItem {
  return {
    id: `race-${round}`,
    season: 2024,
    round,
    raceName: name,
    circuit: null,
    country: null,
    date: null,
    winner: null,
  };
}

function resultsQuery(
  data: SessionResultEntry[] | undefined,
): UseQueryResult<SessionResultEntry[]> {
  return { data } as UseQueryResult<SessionResultEntry[]>;
}

function result(driver: string, gridPosition: number, finishPosition: number): SessionResultEntry {
  return {
    driver,
    team: null,
    gridPosition,
    finishPosition,
    points: null,
    status: null,
    fastestLap: null,
    lapsCompleted: null,
  };
}

describe("buildPaceSeries", () => {
  it("keeps only laps where both driver and teammate have a recorded time", () => {
    const result = buildPaceSeries(
      [lap(1, 90.1), lap(2, 89.5), lap(3, null)],
      [lap(1, 91.0), lap(2, null)],
    );

    // Lap 2 is dropped: teammate's lap 2 has no time. Lap 3 is dropped:
    // the driver's own lap 3 has no time (filtered before intersecting).
    expect(result.categories).toEqual([1]);
    expect(result.driverData).toEqual([90.1]);
    expect(result.teammateData).toEqual([91.0]);
  });

  it("falls back to the driver's own laps alone when there is no teammate data", () => {
    const result = buildPaceSeries([lap(2, 89.5), lap(1, 90.1)], undefined);

    // Sorted by lap number even though input wasn't.
    expect(result.categories).toEqual([1, 2]);
    expect(result.driverData).toEqual([90.1, 89.5]);
    expect(result.teammateData).toBeUndefined();
  });

  it("returns empty series when neither driver nor teammate has any timed laps", () => {
    const result = buildPaceSeries([lap(1, null)], []);

    expect(result.categories).toEqual([]);
    expect(result.driverData).toEqual([]);
    expect(result.teammateData).toEqual([]);
  });
});

describe("extractRoundPositions", () => {
  it("reads the named driver's grid/finish position out of each race's results query", () => {
    const races = [race(1, "Bahrain"), race(2, "Jeddah")];
    const resultsQueries = [
      resultsQuery([result("Max Verstappen", 1, 1)]),
      resultsQuery([result("Charles Leclerc", 2, 2)]),
    ];

    const positions: RoundPosition[] = extractRoundPositions(
      races,
      resultsQueries,
      "Max Verstappen",
    );

    expect(positions).toEqual([
      { round: 1, grid: 1, finish: 1 },
      { round: 2, grid: null, finish: null },
    ]);
  });

  it("returns nulls for a race whose results query has not resolved yet", () => {
    const races = [race(1, "Bahrain")];
    const resultsQueries = [resultsQuery(undefined)];

    const positions = extractRoundPositions(races, resultsQueries, "Max Verstappen");

    expect(positions).toEqual([{ round: 1, grid: null, finish: null }]);
  });
});
