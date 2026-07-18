import type { ConstructorId } from "@pit-wall-insight/ui";

/**
 * SAMPLE DATA — hand-written placeholder values, not real statistics.
 * Every figure here is illustrative until the analytics API exists
 * (apps/backend has no driver endpoints yet); the page renders a visible
 * "Sample data" badge for the same reason. Replace this module with a
 * TanStack Query hook against `/api/v1/drivers/...` when the backend
 * lands — the page consumes only the `DriverProfile` shape, so swapping
 * the source should not touch the components.
 */

export interface DriverProfile {
  id: string;
  name: string;
  abbreviation: string;
  number: number;
  nationality: string;
  constructorId: ConstructorId;
  teamName: string;
  teammateName: string;
  stats: {
    wins: number;
    podiums: number;
    poles: number;
    fastestLaps: number;
  };
  /** Lap times (seconds) across a sample stint. */
  racePace: readonly number[];
  /** Teammate's lap times over the same stint, for head-to-head overlay. */
  teammatePace: readonly number[];
  /** Grid position per round. */
  qualifyingPositions: readonly number[];
  /** Finishing position per round. */
  racePositions: readonly number[];
}

export const SAMPLE_STINT_LAPS: readonly string[] = Array.from(
  { length: 10 },
  (_, i) => `Lap ${i + 1}`,
);

export { SAMPLE_ROUNDS } from "../../constants/season.js";

export const SAMPLE_DRIVERS: readonly DriverProfile[] = [
  {
    id: "verstappen",
    name: "Max Verstappen",
    abbreviation: "VER",
    number: 1,
    nationality: "Netherlands",
    constructorId: "red-bull",
    teamName: "Red Bull",
    teammateName: "Teammate",
    stats: { wins: 5, podiums: 7, poles: 4, fastestLaps: 3 },
    racePace: [88.4, 88.1, 87.9, 87.8, 87.9, 87.7, 87.6, 87.7, 87.5, 87.4],
    teammatePace: [88.9, 88.5, 88.4, 88.2, 88.3, 88.1, 88.0, 88.1, 87.9, 87.9],
    qualifyingPositions: [1, 2, 1, 1, 3, 1, 2, 1],
    racePositions: [1, 1, 2, 1, 4, 1, 2, 1],
  },
  {
    id: "norris",
    name: "Lando Norris",
    abbreviation: "NOR",
    number: 4,
    nationality: "United Kingdom",
    constructorId: "mclaren",
    teamName: "McLaren",
    teammateName: "Teammate",
    stats: { wins: 3, podiums: 6, poles: 2, fastestLaps: 2 },
    racePace: [88.6, 88.2, 88.0, 87.9, 88.0, 87.8, 87.7, 87.8, 87.6, 87.6],
    teammatePace: [88.8, 88.4, 88.2, 88.0, 88.1, 87.9, 87.9, 88.0, 87.8, 87.7],
    qualifyingPositions: [2, 1, 3, 2, 1, 2, 1, 3],
    racePositions: [2, 3, 1, 2, 1, 3, 1, 2],
  },
  {
    id: "leclerc",
    name: "Charles Leclerc",
    abbreviation: "LEC",
    number: 16,
    nationality: "Monaco",
    constructorId: "ferrari",
    teamName: "Ferrari",
    teammateName: "Teammate",
    stats: { wins: 2, podiums: 5, poles: 3, fastestLaps: 1 },
    racePace: [88.7, 88.3, 88.1, 88.0, 88.2, 87.9, 87.8, 87.9, 87.7, 87.8],
    teammatePace: [88.9, 88.6, 88.3, 88.2, 88.3, 88.1, 88.0, 88.2, 87.9, 88.0],
    qualifyingPositions: [3, 4, 2, 3, 2, 4, 3, 1],
    racePositions: [3, 5, 3, 4, 2, 5, 4, 1],
  },
  {
    id: "russell",
    name: "George Russell",
    abbreviation: "RUS",
    number: 63,
    nationality: "United Kingdom",
    constructorId: "mercedes",
    teamName: "Mercedes",
    teammateName: "Teammate",
    stats: { wins: 1, podiums: 4, poles: 1, fastestLaps: 2 },
    racePace: [88.8, 88.5, 88.2, 88.1, 88.3, 88.0, 88.0, 88.1, 87.9, 87.9],
    teammatePace: [89.1, 88.8, 88.5, 88.4, 88.5, 88.2, 88.2, 88.3, 88.1, 88.1],
    qualifyingPositions: [4, 3, 5, 4, 5, 3, 4, 5],
    racePositions: [4, 2, 4, 3, 3, 4, 3, 4],
  },
] as const;

export type SampleDriverId = (typeof SAMPLE_DRIVERS)[number]["id"];

const DRIVER_BY_ID = new Map(SAMPLE_DRIVERS.map((driver) => [driver.id, driver]));

export function getSampleDriver(id: string): DriverProfile | undefined {
  return DRIVER_BY_ID.get(id);
}
