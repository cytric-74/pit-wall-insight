/**
 * `/constructors*` (docs/08_API_SPECIFICATION.md — "Constructors").
 * Mirrors `apps/backend/app/schemas/constructor.py` exactly.
 */

export interface Constructor {
  id: string;
  teamName: string;
  baseCountry: string | null;
  active: boolean | null;
}

export interface ConstructorSeasonSummary {
  season: number;
  wins: number;
  podiums: number;
  pitstopAverage: number | null;
  strategySuccess: number | null;
  averagePoints: number | null;
  dnfRate: number | null;
  developmentIndex: number | null;
  averagePace: number | null;
}

export interface ConstructorCareerStatistics {
  constructor: string;
  seasonsCompeted: number;
  wins: number;
  podiums: number;
  averagePoints: number | null;
  dnfRate: number | null;
}
