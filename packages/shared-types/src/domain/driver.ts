/**
 * `/drivers*` (docs/08_API_SPECIFICATION.md — "Drivers"). Mirrors
 * `apps/backend/app/schemas/driver.py` exactly.
 */

export interface Driver {
  id: string;
  driverNumber: number | null;
  fullName: string;
  abbreviation: string | null;
  nationality: string | null;
  dateOfBirth: string | null;
  teamId: string | null;
  team: string | null;
  rookieSeason: number | null;
  worldTitles: number | null;
  active: boolean | null;
}

export interface DriverCareerStatistics {
  driver: string;
  seasonsCompeted: number;
  wins: number;
  podiums: number;
  poles: number;
  fastestLaps: number;
  averageFinish: number | null;
  consistencyScore: number | null;
}

export interface DriverLap {
  season: number;
  round: number;
  raceName: string | null;
  sessionType: string;
  lapNumber: number;
  lapTime: number | null;
  sector1: number | null;
  sector2: number | null;
  sector3: number | null;
  compound: string | null;
  tyreLife: number | null;
  position: number | null;
  pitIn: boolean | null;
  pitOut: boolean | null;
}

export interface SeasonConsistencyEntry {
  season: number;
  consistencyScore: number | null;
  averageFinish: number | null;
}

export interface DriverConsistency {
  driver: string;
  careerConsistencyScore: number | null;
  seasons: SeasonConsistencyEntry[];
}

export interface DriverComparisonEntry {
  driver: string;
  wins: number;
  podiums: number;
  poles: number;
  fastestLaps: number;
  averageFinish: number | null;
  averageQualifying: number | null;
  consistencyScore: number | null;
  pitEfficiency: number | null;
  racePace: number | null;
  qualifyingPace: number | null;
}

export interface DriverComparison {
  season: number;
  driverA: DriverComparisonEntry;
  driverB: DriverComparisonEntry;
}
