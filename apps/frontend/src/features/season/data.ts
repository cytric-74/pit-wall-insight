import type { ConstructorId } from "@pit-wall-insight/ui";

import { SAMPLE_ROUNDS } from "../../constants/season.js";

/**
 * SAMPLE DATA — hand-written placeholder values, not real championship
 * records. The page shows a visible "Sample data" badge for the same
 * reason. Replace this module with a TanStack Query hook against
 * `/api/v1/seasons/...` once the backend exists — the page consumes
 * only the `SeasonSummary` shape, so swapping the source should not
 * touch the components.
 */

export interface DriverStanding {
  driver: string;
  abbreviation: string;
  constructorId: ConstructorId;
  /** Cumulative championship points after each round. */
  progression: readonly number[];
}

export interface ConstructorStanding {
  constructorId: ConstructorId;
  name: string;
  progression: readonly number[];
  wins: number;
}

export interface CalendarRace {
  round: string;
  name: string;
  circuit: string;
  date: string;
  winner: string;
}

export interface SeasonSummary {
  id: string;
  year: number;
  /** Whether the season has concluded — changes "Leader" to "Champion" in the UI. */
  completed: boolean;
  driverStandings: readonly DriverStanding[];
  constructorStandings: readonly ConstructorStanding[];
  calendar: readonly CalendarRace[];
}

export { SAMPLE_ROUNDS };

export const SAMPLE_SEASONS: readonly SeasonSummary[] = [
  {
    id: "2026",
    year: 2026,
    completed: false,
    driverStandings: [
      {
        driver: "Verstappen",
        abbreviation: "VER",
        constructorId: "red-bull",
        progression: [25, 43, 69, 94, 102, 128, 151, 176],
      },
      {
        driver: "Norris",
        abbreviation: "NOR",
        constructorId: "mclaren",
        progression: [18, 39, 58, 76, 101, 120, 141, 158],
      },
      {
        driver: "Leclerc",
        abbreviation: "LEC",
        constructorId: "ferrari",
        progression: [16, 28, 44, 63, 81, 96, 110, 132],
      },
      {
        driver: "Russell",
        abbreviation: "RUS",
        constructorId: "mercedes",
        progression: [12, 22, 33, 47, 60, 74, 87, 101],
      },
    ],
    constructorStandings: [
      {
        constructorId: "red-bull",
        name: "Red Bull",
        progression: [43, 76, 120, 158, 178, 220, 255, 296],
        wins: 5,
      },
      {
        constructorId: "mclaren",
        name: "McLaren",
        progression: [30, 64, 98, 127, 163, 192, 224, 254],
        wins: 3,
      },
      {
        constructorId: "ferrari",
        name: "Ferrari",
        progression: [28, 50, 79, 108, 132, 156, 178, 208],
        wins: 2,
      },
      {
        constructorId: "mercedes",
        name: "Mercedes",
        progression: [20, 36, 54, 74, 92, 112, 130, 152],
        wins: 1,
      },
    ],
    calendar: [
      {
        round: "BHR",
        name: "Bahrain Grand Prix",
        circuit: "Bahrain International Circuit",
        date: "2 Mar 2026",
        winner: "M. Verstappen",
      },
      {
        round: "SAU",
        name: "Saudi Arabian Grand Prix",
        circuit: "Jeddah Corniche Circuit",
        date: "9 Mar 2026",
        winner: "M. Verstappen",
      },
      {
        round: "AUS",
        name: "Australian Grand Prix",
        circuit: "Albert Park Circuit",
        date: "23 Mar 2026",
        winner: "L. Norris",
      },
      {
        round: "JPN",
        name: "Japanese Grand Prix",
        circuit: "Suzuka International Racing Course",
        date: "6 Apr 2026",
        winner: "M. Verstappen",
      },
      {
        round: "CHN",
        name: "Chinese Grand Prix",
        circuit: "Shanghai International Circuit",
        date: "20 Apr 2026",
        winner: "L. Norris",
      },
      {
        round: "MIA",
        name: "Miami Grand Prix",
        circuit: "Miami International Autodrome",
        date: "4 May 2026",
        winner: "M. Verstappen",
      },
      {
        round: "EMI",
        name: "Emilia Romagna Grand Prix",
        circuit: "Autodromo Enzo e Dino Ferrari",
        date: "18 May 2026",
        winner: "M. Verstappen",
      },
      {
        round: "MON",
        name: "Monaco Grand Prix",
        circuit: "Circuit de Monaco",
        date: "24 May 2026",
        winner: "C. Leclerc",
      },
    ],
  },
  {
    id: "2025",
    year: 2025,
    completed: true,
    driverStandings: [
      {
        driver: "Norris",
        abbreviation: "NOR",
        constructorId: "mclaren",
        progression: [18, 45, 79, 118, 154, 189, 231, 268],
      },
      {
        driver: "Verstappen",
        abbreviation: "VER",
        constructorId: "red-bull",
        progression: [26, 51, 74, 105, 143, 176, 210, 255],
      },
      {
        driver: "Leclerc",
        abbreviation: "LEC",
        constructorId: "ferrari",
        progression: [15, 33, 55, 84, 112, 138, 165, 194],
      },
      {
        driver: "Russell",
        abbreviation: "RUS",
        constructorId: "mercedes",
        progression: [10, 24, 40, 62, 84, 104, 126, 148],
      },
    ],
    constructorStandings: [
      {
        constructorId: "mclaren",
        name: "McLaren",
        progression: [32, 82, 140, 205, 265, 320, 388, 452],
        wins: 6,
      },
      {
        constructorId: "red-bull",
        name: "Red Bull",
        progression: [46, 88, 126, 176, 234, 288, 340, 408],
        wins: 4,
      },
      {
        constructorId: "ferrari",
        name: "Ferrari",
        progression: [26, 56, 92, 138, 178, 218, 258, 300],
        wins: 1,
      },
      {
        constructorId: "mercedes",
        name: "Mercedes",
        progression: [18, 40, 66, 100, 132, 164, 196, 228],
        wins: 0,
      },
    ],
    calendar: [
      {
        round: "BHR",
        name: "Bahrain Grand Prix",
        circuit: "Bahrain International Circuit",
        date: "3 Mar 2025",
        winner: "L. Norris",
      },
      {
        round: "SAU",
        name: "Saudi Arabian Grand Prix",
        circuit: "Jeddah Corniche Circuit",
        date: "10 Mar 2025",
        winner: "M. Verstappen",
      },
      {
        round: "AUS",
        name: "Australian Grand Prix",
        circuit: "Albert Park Circuit",
        date: "24 Mar 2025",
        winner: "L. Norris",
      },
      {
        round: "JPN",
        name: "Japanese Grand Prix",
        circuit: "Suzuka International Racing Course",
        date: "7 Apr 2025",
        winner: "M. Verstappen",
      },
      {
        round: "CHN",
        name: "Chinese Grand Prix",
        circuit: "Shanghai International Circuit",
        date: "21 Apr 2025",
        winner: "L. Norris",
      },
      {
        round: "MIA",
        name: "Miami Grand Prix",
        circuit: "Miami International Autodrome",
        date: "5 May 2025",
        winner: "L. Norris",
      },
      {
        round: "EMI",
        name: "Emilia Romagna Grand Prix",
        circuit: "Autodromo Enzo e Dino Ferrari",
        date: "19 May 2025",
        winner: "L. Norris",
      },
      {
        round: "MON",
        name: "Monaco Grand Prix",
        circuit: "Circuit de Monaco",
        date: "25 May 2025",
        winner: "C. Leclerc",
      },
    ],
  },
] as const;

const SEASON_BY_ID = new Map(SAMPLE_SEASONS.map((season) => [season.id, season]));

export function getSampleSeason(id: string): SeasonSummary | undefined {
  return SEASON_BY_ID.get(id);
}
