import type { ConstructorId } from "@pit-wall-insight/ui";

/**
 * SAMPLE DATA — hand-written placeholder values, not a real race record.
 * The page shows a visible "Sample data" badge for the same reason.
 * Replace this module with a TanStack Query hook against
 * `/api/v1/races/...` once the backend exists — the page consumes only
 * the `RaceSummary` shape, so swapping the source should not touch the
 * components.
 */

export interface RaceDriverTrace {
  driver: string;
  abbreviation: string;
  constructorId: ConstructorId;
  /** Position held after each lap. */
  positions: readonly number[];
}

export interface RaceEvent {
  lap: number;
  label: string;
}

export interface RaceSummary {
  id: string;
  name: string;
  circuit: string;
  date: string;
  laps: number;
  stats: {
    winner: string;
    polePosition: string;
    fastestLap: string;
    safetyCarLaps: number;
  };
  drivers: readonly RaceDriverTrace[];
  /** Track temperature (°C) at each lap — "Weather evolution". */
  trackTemperature: readonly number[];
  pitStopLabels: readonly string[];
  pitStopDurations: readonly number[];
  events: readonly RaceEvent[];
}

export const SAMPLE_RACE_LAPS: readonly string[] = Array.from(
  { length: 10 },
  (_, i) => `Lap ${i + 1}`,
);

export const SAMPLE_RACES: readonly RaceSummary[] = [
  {
    id: "bahrain",
    name: "Bahrain Grand Prix",
    circuit: "Bahrain International Circuit",
    date: "2 Mar 2026",
    laps: 57,
    stats: {
      winner: "M. Verstappen",
      polePosition: "M. Verstappen",
      fastestLap: "1:32.741",
      safetyCarLaps: 3,
    },
    drivers: [
      {
        driver: "Verstappen",
        abbreviation: "VER",
        constructorId: "red-bull",
        positions: [1, 1, 1, 1, 2, 1, 1, 1, 1, 1],
      },
      {
        driver: "Norris",
        abbreviation: "NOR",
        constructorId: "mclaren",
        positions: [3, 2, 2, 2, 1, 2, 2, 2, 2, 2],
      },
      {
        driver: "Leclerc",
        abbreviation: "LEC",
        constructorId: "ferrari",
        positions: [2, 3, 3, 3, 3, 3, 3, 3, 3, 3],
      },
      {
        driver: "Russell",
        abbreviation: "RUS",
        constructorId: "mercedes",
        positions: [4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
      },
    ],
    trackTemperature: [34, 35, 36, 37, 38, 38, 37, 36, 35, 34],
    pitStopLabels: ["VER Lap 3", "NOR Lap 4", "LEC Lap 4", "RUS Lap 5"],
    pitStopDurations: [2.3, 2.1, 2.5, 2.4],
    events: [
      { lap: 1, label: "Race start" },
      { lap: 3, label: "Verstappen pits for hard tyres" },
      { lap: 5, label: "Safety Car — debris, Turn 4" },
      { lap: 8, label: "Norris sets fastest lap" },
      { lap: 10, label: "Race finish" },
    ],
  },
  {
    id: "monaco",
    name: "Monaco Grand Prix",
    circuit: "Circuit de Monaco",
    date: "24 May 2026",
    laps: 78,
    stats: {
      winner: "C. Leclerc",
      polePosition: "C. Leclerc",
      fastestLap: "1:12.909",
      safetyCarLaps: 6,
    },
    drivers: [
      {
        driver: "Leclerc",
        abbreviation: "LEC",
        constructorId: "ferrari",
        positions: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
      },
      {
        driver: "Verstappen",
        abbreviation: "VER",
        constructorId: "red-bull",
        positions: [2, 2, 2, 3, 2, 2, 2, 2, 2, 2],
      },
      {
        driver: "Norris",
        abbreviation: "NOR",
        constructorId: "mclaren",
        positions: [3, 3, 3, 2, 3, 3, 3, 3, 3, 3],
      },
      {
        driver: "Russell",
        abbreviation: "RUS",
        constructorId: "mercedes",
        positions: [4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
      },
    ],
    trackTemperature: [28, 29, 30, 31, 32, 32, 31, 30, 29, 28],
    pitStopLabels: ["LEC Lap 2", "VER Lap 3", "NOR Lap 3", "RUS Lap 4"],
    pitStopDurations: [2.6, 2.4, 2.7, 2.5],
    events: [
      { lap: 1, label: "Race start" },
      { lap: 2, label: "Leclerc pits under Virtual Safety Car" },
      { lap: 4, label: "Safety Car — contact, Turn 1" },
      { lap: 7, label: "Rain begins at Casino Square" },
      { lap: 10, label: "Race finish" },
    ],
  },
  {
    id: "silverstone",
    name: "British Grand Prix",
    circuit: "Silverstone Circuit",
    date: "5 Jul 2026",
    laps: 52,
    stats: {
      winner: "L. Norris",
      polePosition: "L. Norris",
      fastestLap: "1:27.097",
      safetyCarLaps: 0,
    },
    drivers: [
      {
        driver: "Norris",
        abbreviation: "NOR",
        constructorId: "mclaren",
        positions: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
      },
      {
        driver: "Verstappen",
        abbreviation: "VER",
        constructorId: "red-bull",
        positions: [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
      },
      {
        driver: "Leclerc",
        abbreviation: "LEC",
        constructorId: "ferrari",
        positions: [4, 4, 3, 3, 3, 3, 3, 3, 3, 3],
      },
      {
        driver: "Russell",
        abbreviation: "RUS",
        constructorId: "mercedes",
        positions: [3, 3, 4, 4, 4, 4, 4, 4, 4, 4],
      },
    ],
    trackTemperature: [22, 22, 23, 24, 24, 23, 23, 22, 22, 21],
    pitStopLabels: ["NOR Lap 4", "VER Lap 4", "RUS Lap 5", "LEC Lap 5"],
    pitStopDurations: [2.2, 2.1, 2.3, 2.4],
    events: [
      { lap: 1, label: "Race start" },
      { lap: 4, label: "Norris and Verstappen pit in the same lap" },
      { lap: 6, label: "Leclerc passes Russell for P3" },
      { lap: 9, label: "Norris sets fastest lap" },
      { lap: 10, label: "Race finish" },
    ],
  },
] as const;

const RACE_BY_ID = new Map(SAMPLE_RACES.map((race) => [race.id, race]));

export function getSampleRace(id: string): RaceSummary | undefined {
  return RACE_BY_ID.get(id);
}
