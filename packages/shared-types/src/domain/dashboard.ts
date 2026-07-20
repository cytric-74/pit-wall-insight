/**
 * `/dashboard` and `/dashboard/highlights` (docs/08_API_SPECIFICATION.md —
 * "Dashboard"). Mirrors `apps/backend/app/schemas/dashboard.py` and
 * `apps/backend/app/schemas/season.py`'s standing-entry shapes exactly —
 * field names are camelCase here because the backend's `CamelModel` base
 * (`apps/backend/app/schemas/base.py`) serializes every response that way.
 */

export interface DriverStandingEntry {
  position: number;
  driver: string;
  team: string | null;
  points: number;
  wins: number;
}

export interface ConstructorStandingEntry {
  position: number;
  constructor: string;
  points: number;
  wins: number;
}

export interface RecentRace {
  round: number;
  raceName: string | null;
  winner: string | null;
  date: string | null;
}

export interface DashboardData {
  season: number;
  championDriver: string | null;
  championConstructor: string | null;
  driverStandings: DriverStandingEntry[];
  constructorStandings: ConstructorStandingEntry[];
  recentRaces: RecentRace[];
  fastestLapDriver: string | null;
  fastestLapTime: number | null;
  fastestPitstop: number | null;
  averageOvertakes: number | null;
  championshipGap: number | null;
}

export interface DashboardHighlights {
  raceName: string | null;
  winner: string | null;
  pole: string | null;
  fastestLap: string | null;
  retirements: number | null;
  weather: string | null;
}
