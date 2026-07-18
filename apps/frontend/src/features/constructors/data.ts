import type { ConstructorId } from "@pit-wall-insight/ui";

/**
 * SAMPLE DATA — hand-written placeholder values, not real statistics.
 * The page shows a visible "Sample data" badge for the same reason.
 * Replace this module with a TanStack Query hook against
 * `/api/v1/constructors/...` once the backend exists — the page consumes
 * only the `ConstructorProfile` shape, so swapping the source should not
 * touch the components.
 */

export interface ConstructorDriverSummary {
  name: string;
  abbreviation: string;
  /** Points scored per round (not cumulative). */
  pointsPerRound: readonly number[];
}

export interface ConstructorProfile {
  id: ConstructorId;
  name: string;
  base: string;
  powerUnit: string;
  stats: {
    wins: number;
    podiums: number;
    poles: number;
    points: number;
  };
  /** Championship points after each round (cumulative). */
  cumulativePoints: readonly number[];
  /** Average pit stop time per round (seconds). */
  averagePitStops: readonly number[];
  drivers: readonly [ConstructorDriverSummary, ConstructorDriverSummary];
  reliability: {
    classifiedFinishes: string;
    dnfs: number;
    lapsCompletedPct: string;
  };
}

export const SAMPLE_CONSTRUCTORS: readonly ConstructorProfile[] = [
  {
    id: "red-bull",
    name: "Red Bull",
    base: "Milton Keynes, UK",
    powerUnit: "Honda RBPT",
    stats: { wins: 5, podiums: 9, poles: 5, points: 261 },
    cumulativePoints: [43, 77, 112, 155, 178, 214, 236, 261],
    averagePitStops: [2.3, 2.2, 2.4, 2.1, 2.3, 2.2, 2.1, 2.2],
    drivers: [
      {
        name: "Max Verstappen",
        abbreviation: "VER",
        pointsPerRound: [25, 25, 18, 25, 12, 25, 18, 25],
      },
      { name: "Teammate", abbreviation: "TM2", pointsPerRound: [18, 9, 17, 18, 11, 11, 4, 8] },
    ],
    reliability: { classifiedFinishes: "15 / 16", dnfs: 1, lapsCompletedPct: "98%" },
  },
  {
    id: "mclaren",
    name: "McLaren",
    base: "Woking, UK",
    powerUnit: "Mercedes",
    stats: { wins: 4, podiums: 10, poles: 3, points: 254 },
    cumulativePoints: [37, 73, 111, 141, 181, 203, 233, 254],
    averagePitStops: [2.2, 2.3, 2.2, 2.4, 2.2, 2.3, 2.2, 2.3],
    drivers: [
      {
        name: "Lando Norris",
        abbreviation: "NOR",
        pointsPerRound: [18, 25, 15, 18, 25, 15, 25, 18],
      },
      { name: "Teammate", abbreviation: "TM2", pointsPerRound: [19, 11, 23, 12, 15, 7, 5, 3] },
    ],
    reliability: { classifiedFinishes: "16 / 16", dnfs: 0, lapsCompletedPct: "100%" },
  },
  {
    id: "ferrari",
    name: "Ferrari",
    base: "Maranello, Italy",
    powerUnit: "Ferrari",
    stats: { wins: 3, podiums: 8, poles: 4, points: 228 },
    cumulativePoints: [30, 58, 88, 110, 148, 170, 196, 228],
    averagePitStops: [2.4, 2.3, 2.5, 2.3, 2.4, 2.2, 2.3, 2.4],
    drivers: [
      {
        name: "Charles Leclerc",
        abbreviation: "LEC",
        pointsPerRound: [15, 10, 15, 12, 18, 10, 12, 25],
      },
      { name: "Teammate", abbreviation: "TM2", pointsPerRound: [15, 18, 15, 10, 20, 12, 14, 7] },
    ],
    reliability: { classifiedFinishes: "14 / 16", dnfs: 2, lapsCompletedPct: "95%" },
  },
  {
    id: "mercedes",
    name: "Mercedes",
    base: "Brackley, UK",
    powerUnit: "Mercedes",
    stats: { wins: 1, podiums: 6, poles: 1, points: 172 },
    cumulativePoints: [22, 48, 68, 92, 114, 130, 152, 172],
    averagePitStops: [2.5, 2.4, 2.4, 2.5, 2.3, 2.4, 2.5, 2.4],
    drivers: [
      {
        name: "George Russell",
        abbreviation: "RUS",
        pointsPerRound: [12, 18, 12, 15, 15, 12, 15, 12],
      },
      { name: "Teammate", abbreviation: "TM2", pointsPerRound: [10, 8, 8, 9, 7, 4, 7, 8] },
    ],
    reliability: { classifiedFinishes: "15 / 16", dnfs: 1, lapsCompletedPct: "97%" },
  },
] as const;

const CONSTRUCTOR_BY_ID = new Map(SAMPLE_CONSTRUCTORS.map((team) => [team.id, team]));

export function getSampleConstructor(id: string): ConstructorProfile | undefined {
  return CONSTRUCTOR_BY_ID.get(id as ConstructorId);
}
