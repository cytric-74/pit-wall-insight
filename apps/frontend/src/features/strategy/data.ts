import type { ConstructorId } from "@pit-wall-insight/ui";

/**
 * SAMPLE DATA — hand-written placeholder values, not a real strategy
 * model. The page shows a visible "Sample data" badge for the same
 * reason. Replace this module with a TanStack Query hook against
 * `/api/v1/strategy/...` (`fct_strategy`, `fct_pitstop`) once the
 * backend exists — the page consumes only the `RaceStrategy` shape, so
 * swapping the source should not touch the components.
 */

export type Compound = "Soft" | "Medium" | "Hard";

export interface Stint {
  compound: Compound;
  startLap: number;
  endLap: number;
  averagePace: number;
}

export interface PitStopRecord {
  lap: number;
  optimalWindow: readonly [number, number];
}

export interface DriverStrategy {
  driver: string;
  abbreviation: string;
  constructorId: ConstructorId;
  stints: readonly Stint[];
  pitStops: readonly PitStopRecord[];
}

export interface StrategyAttempt {
  label: string;
  netGainSeconds: number;
}

export interface CompoundEffectiveness {
  compound: Compound;
  averagePaceSeconds: number;
}

export interface StrategySimulation {
  label: string;
  totalRaceTimeSeconds: number;
}

export interface RaceStrategy {
  id: string;
  raceName: string;
  circuit: string;
  laps: number;
  degradationLaps: readonly number[];
  degradationByCompound: Readonly<Record<Compound, readonly number[]>>;
  drivers: readonly DriverStrategy[];
  undercuts: readonly StrategyAttempt[];
  overcuts: readonly StrategyAttempt[];
  compoundEffectiveness: readonly CompoundEffectiveness[];
  simulations: readonly StrategySimulation[];
}

export const STINT_LAP_MARKERS: readonly string[] = Array.from(
  { length: 10 },
  (_, i) => `+${i + 1}`,
);

export const SAMPLE_STRATEGIES: readonly RaceStrategy[] = [
  {
    id: "bahrain",
    raceName: "Bahrain Grand Prix",
    circuit: "Bahrain International Circuit",
    laps: 57,
    degradationLaps: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    degradationByCompound: {
      Soft: [0, 0.1, 0.25, 0.45, 0.7, 1.0, 1.35, 1.75, 2.2, 2.7],
      Medium: [0, 0.05, 0.12, 0.22, 0.35, 0.5, 0.68, 0.88, 1.1, 1.35],
      Hard: [0, 0.02, 0.05, 0.09, 0.14, 0.2, 0.27, 0.35, 0.44, 0.54],
    },
    drivers: [
      {
        driver: "Verstappen",
        abbreviation: "VER",
        constructorId: "red-bull",
        stints: [
          { compound: "Medium", startLap: 1, endLap: 18, averagePace: 92.1 },
          { compound: "Hard", startLap: 19, endLap: 40, averagePace: 93.4 },
          { compound: "Soft", startLap: 41, endLap: 57, averagePace: 91.8 },
        ],
        pitStops: [
          { lap: 18, optimalWindow: [16, 19] },
          { lap: 40, optimalWindow: [39, 42] },
        ],
      },
      {
        driver: "Norris",
        abbreviation: "NOR",
        constructorId: "mclaren",
        stints: [
          { compound: "Medium", startLap: 1, endLap: 20, averagePace: 92.3 },
          { compound: "Hard", startLap: 21, endLap: 57, averagePace: 93.6 },
        ],
        pitStops: [{ lap: 20, optimalWindow: [16, 19] }],
      },
      {
        driver: "Leclerc",
        abbreviation: "LEC",
        constructorId: "ferrari",
        stints: [
          { compound: "Soft", startLap: 1, endLap: 15, averagePace: 91.6 },
          { compound: "Medium", startLap: 16, endLap: 38, averagePace: 92.5 },
          { compound: "Hard", startLap: 39, endLap: 57, averagePace: 93.5 },
        ],
        pitStops: [
          { lap: 15, optimalWindow: [16, 19] },
          { lap: 38, optimalWindow: [39, 42] },
        ],
      },
    ],
    undercuts: [
      { label: "VER undercuts LEC — Lap 18", netGainSeconds: 2.4 },
      { label: "NOR undercuts VER — Lap 20", netGainSeconds: -1.1 },
    ],
    overcuts: [
      { label: "NOR overcuts VER — Lap 20", netGainSeconds: 1.8 },
      { label: "LEC overcuts NOR — Lap 38", netGainSeconds: -0.6 },
    ],
    compoundEffectiveness: [
      { compound: "Soft", averagePaceSeconds: 91.7 },
      { compound: "Medium", averagePaceSeconds: 92.3 },
      { compound: "Hard", averagePaceSeconds: 93.5 },
    ],
    simulations: [
      { label: "One-stop (Medium–Hard)", totalRaceTimeSeconds: 5320.4 },
      { label: "Two-stop (Medium–Hard–Soft)", totalRaceTimeSeconds: 5301.2 },
    ],
  },
  {
    id: "monaco",
    raceName: "Monaco Grand Prix",
    circuit: "Circuit de Monaco",
    laps: 78,
    degradationLaps: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    degradationByCompound: {
      Soft: [0, 0.08, 0.18, 0.32, 0.5, 0.72, 0.98, 1.28, 1.62, 2.0],
      Medium: [0, 0.04, 0.09, 0.16, 0.25, 0.36, 0.49, 0.64, 0.81, 1.0],
      Hard: [0, 0.02, 0.04, 0.07, 0.11, 0.16, 0.22, 0.29, 0.37, 0.46],
    },
    drivers: [
      {
        driver: "Leclerc",
        abbreviation: "LEC",
        constructorId: "ferrari",
        stints: [
          { compound: "Medium", startLap: 1, endLap: 40, averagePace: 73.1 },
          { compound: "Hard", startLap: 41, endLap: 78, averagePace: 74.0 },
        ],
        pitStops: [{ lap: 40, optimalWindow: [38, 42] }],
      },
      {
        driver: "Verstappen",
        abbreviation: "VER",
        constructorId: "red-bull",
        stints: [
          { compound: "Medium", startLap: 1, endLap: 38, averagePace: 73.3 },
          { compound: "Hard", startLap: 39, endLap: 78, averagePace: 74.1 },
        ],
        pitStops: [{ lap: 38, optimalWindow: [38, 42] }],
      },
      {
        driver: "Norris",
        abbreviation: "NOR",
        constructorId: "mclaren",
        stints: [
          { compound: "Medium", startLap: 1, endLap: 42, averagePace: 73.4 },
          { compound: "Hard", startLap: 43, endLap: 78, averagePace: 74.2 },
        ],
        pitStops: [{ lap: 42, optimalWindow: [38, 42] }],
      },
    ],
    undercuts: [{ label: "VER undercuts LEC — Lap 38", netGainSeconds: 3.2 }],
    overcuts: [{ label: "NOR overcuts VER — Lap 42", netGainSeconds: -1.4 }],
    compoundEffectiveness: [
      { compound: "Soft", averagePaceSeconds: 72.6 },
      { compound: "Medium", averagePaceSeconds: 73.3 },
      { compound: "Hard", averagePaceSeconds: 74.1 },
    ],
    simulations: [
      { label: "One-stop (Medium–Hard)", totalRaceTimeSeconds: 5771.8 },
      { label: "Two-stop (Soft–Medium–Hard)", totalRaceTimeSeconds: 5789.5 },
    ],
  },
  {
    id: "silverstone",
    raceName: "British Grand Prix",
    circuit: "Silverstone Circuit",
    laps: 52,
    degradationLaps: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    degradationByCompound: {
      Soft: [0, 0.12, 0.28, 0.5, 0.78, 1.12, 1.5, 1.94, 2.44, 3.0],
      Medium: [0, 0.06, 0.14, 0.25, 0.4, 0.58, 0.79, 1.03, 1.3, 1.6],
      Hard: [0, 0.03, 0.06, 0.11, 0.17, 0.24, 0.33, 0.43, 0.54, 0.67],
    },
    drivers: [
      {
        driver: "Norris",
        abbreviation: "NOR",
        constructorId: "mclaren",
        stints: [
          { compound: "Medium", startLap: 1, endLap: 22, averagePace: 88.4 },
          { compound: "Hard", startLap: 23, endLap: 52, averagePace: 89.6 },
        ],
        pitStops: [{ lap: 22, optimalWindow: [20, 24] }],
      },
      {
        driver: "Verstappen",
        abbreviation: "VER",
        constructorId: "red-bull",
        stints: [
          { compound: "Medium", startLap: 1, endLap: 24, averagePace: 88.6 },
          { compound: "Hard", startLap: 25, endLap: 52, averagePace: 89.8 },
        ],
        pitStops: [{ lap: 24, optimalWindow: [20, 24] }],
      },
      {
        driver: "Leclerc",
        abbreviation: "LEC",
        constructorId: "ferrari",
        stints: [
          { compound: "Soft", startLap: 1, endLap: 18, averagePace: 87.9 },
          { compound: "Medium", startLap: 19, endLap: 40, averagePace: 88.7 },
          { compound: "Hard", startLap: 41, endLap: 52, averagePace: 89.7 },
        ],
        pitStops: [
          { lap: 18, optimalWindow: [20, 24] },
          { lap: 40, optimalWindow: [38, 42] },
        ],
      },
    ],
    undercuts: [{ label: "NOR undercuts VER — Lap 22", netGainSeconds: 1.9 }],
    overcuts: [{ label: "VER overcuts NOR — Lap 24", netGainSeconds: -0.5 }],
    compoundEffectiveness: [
      { compound: "Soft", averagePaceSeconds: 87.9 },
      { compound: "Medium", averagePaceSeconds: 88.6 },
      { compound: "Hard", averagePaceSeconds: 89.7 },
    ],
    simulations: [
      { label: "One-stop (Medium–Hard)", totalRaceTimeSeconds: 4640.6 },
      { label: "Two-stop (Soft–Medium–Hard)", totalRaceTimeSeconds: 4625.9 },
    ],
  },
] as const;

const STRATEGY_BY_ID = new Map(SAMPLE_STRATEGIES.map((strategy) => [strategy.id, strategy]));

export function getSampleStrategy(id: string): RaceStrategy | undefined {
  return STRATEGY_BY_ID.get(id);
}
