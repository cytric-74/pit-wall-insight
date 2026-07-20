/**
 * `/compare/*` (docs/08_API_SPECIFICATION.md — "Comparison"). Mirrors
 * `apps/backend/app/schemas/compare.py` exactly. `/compare/drivers` reuses
 * `DriverComparison` from `./driver.ts` (the same shape
 * `/drivers/{id}/comparison/{otherId}` already returns) rather than
 * duplicating it here.
 */

import type { RaceSummary } from "./race.js";

export interface ConstructorComparisonEntry {
  constructor: string;
  wins: number;
  podiums: number;
  pitstopAverage: number | null;
  strategySuccess: number | null;
  averagePoints: number | null;
  dnfRate: number | null;
  developmentIndex: number | null;
  averagePace: number | null;
}

export interface ConstructorComparison {
  season: number;
  constructorA: ConstructorComparisonEntry;
  constructorB: ConstructorComparisonEntry;
}

export interface RaceComparison {
  raceA: RaceSummary;
  raceB: RaceSummary;
}
