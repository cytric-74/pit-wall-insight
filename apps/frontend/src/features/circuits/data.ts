/**
 * SAMPLE DATA — hand-written placeholder values, not real circuit records.
 * The page shows a visible "Sample data" badge for the same reason.
 * Replace this module with a TanStack Query hook against
 * `/api/v1/circuits/...` once the backend exists — the page consumes
 * only the `CircuitProfile` shape, so swapping the source should not
 * touch the components.
 */

export interface CircuitCorner {
  number: number;
  name: string;
  sector: 1 | 2 | 3;
}

export interface CircuitWinner {
  season: string;
  driver: string;
  constructorName: string;
}

export interface CircuitProfile {
  id: string;
  name: string;
  country: string;
  city: string;
  lengthKm: number;
  corners: number;
  drsZones: number;
  lapRecord: string;
  direction: "Clockwise" | "Anti-clockwise";
  /** Relative elevation (m) at 10 evenly spaced points around the lap. */
  elevationProfile: readonly number[];
  cornerInfo: readonly CircuitCorner[];
  historicalWinners: readonly CircuitWinner[];
  /** Which abstract placeholder track outline to draw — see TrackShape. */
  trackShape: "loop" | "chicane" | "oval";
}

export const LAP_DISTANCE_MARKERS: readonly string[] = [
  "0%",
  "10%",
  "20%",
  "30%",
  "40%",
  "50%",
  "60%",
  "70%",
  "80%",
  "90%",
];

export const SAMPLE_CIRCUITS: readonly CircuitProfile[] = [
  {
    id: "bahrain",
    name: "Bahrain International Circuit",
    country: "Bahrain",
    city: "Sakhir",
    lengthKm: 5.412,
    corners: 15,
    drsZones: 3,
    lapRecord: "1:31.447 — P. Fittipaldi (2021)",
    direction: "Clockwise",
    elevationProfile: [8, 10, 14, 12, 9, 6, 5, 7, 9, 8],
    cornerInfo: [
      { number: 1, name: "Turn 1", sector: 1 },
      { number: 4, name: "Turn 4", sector: 1 },
      { number: 8, name: "Turn 8", sector: 2 },
      { number: 10, name: "Turn 10", sector: 2 },
      { number: 13, name: "Turn 13", sector: 3 },
    ],
    historicalWinners: [
      { season: "2025", driver: "M. Verstappen", constructorName: "Red Bull" },
      { season: "2024", driver: "M. Verstappen", constructorName: "Red Bull" },
      { season: "2023", driver: "M. Verstappen", constructorName: "Red Bull" },
    ],
    trackShape: "loop",
  },
  {
    id: "monaco",
    name: "Circuit de Monaco",
    country: "Monaco",
    city: "Monte Carlo",
    lengthKm: 3.337,
    corners: 19,
    drsZones: 1,
    lapRecord: "1:12.909 — L. Hamilton (2021)",
    direction: "Clockwise",
    elevationProfile: [12, 18, 24, 30, 26, 20, 22, 28, 20, 14],
    cornerInfo: [
      { number: 1, name: "Sainte Devote", sector: 1 },
      { number: 6, name: "Casino Square", sector: 1 },
      { number: 10, name: "Mirabeau", sector: 2 },
      { number: 15, name: "Swimming Pool", sector: 3 },
      { number: 19, name: "Rascasse", sector: 3 },
    ],
    historicalWinners: [
      { season: "2025", driver: "C. Leclerc", constructorName: "Ferrari" },
      { season: "2024", driver: "C. Leclerc", constructorName: "Ferrari" },
      { season: "2023", driver: "M. Verstappen", constructorName: "Red Bull" },
    ],
    trackShape: "chicane",
  },
  {
    id: "silverstone",
    name: "Silverstone Circuit",
    country: "United Kingdom",
    city: "Silverstone",
    lengthKm: 5.891,
    corners: 18,
    drsZones: 2,
    lapRecord: "1:27.097 — L. Norris (2026)",
    direction: "Clockwise",
    elevationProfile: [15, 13, 11, 9, 12, 16, 14, 10, 8, 13],
    cornerInfo: [
      { number: 1, name: "Abbey", sector: 1 },
      { number: 9, name: "Copse", sector: 1 },
      { number: 11, name: "Maggotts", sector: 2 },
      { number: 12, name: "Becketts", sector: 2 },
      { number: 15, name: "Stowe", sector: 3 },
    ],
    historicalWinners: [
      { season: "2025", driver: "L. Norris", constructorName: "McLaren" },
      { season: "2024", driver: "L. Hamilton", constructorName: "Mercedes" },
      { season: "2023", driver: "M. Verstappen", constructorName: "Red Bull" },
    ],
    trackShape: "oval",
  },
  {
    id: "spa",
    name: "Circuit de Spa-Francorchamps",
    country: "Belgium",
    city: "Stavelot",
    lengthKm: 7.004,
    corners: 20,
    drsZones: 2,
    lapRecord: "1:46.286 — V. Bottas (2018)",
    direction: "Clockwise",
    elevationProfile: [20, 32, 45, 38, 30, 22, 18, 24, 28, 22],
    cornerInfo: [
      { number: 1, name: "La Source", sector: 1 },
      { number: 3, name: "Eau Rouge", sector: 1 },
      { number: 4, name: "Raidillon", sector: 1 },
      { number: 9, name: "Les Combes", sector: 2 },
      { number: 19, name: "Blanchimont", sector: 3 },
    ],
    historicalWinners: [
      { season: "2025", driver: "M. Verstappen", constructorName: "Red Bull" },
      { season: "2024", driver: "L. Norris", constructorName: "McLaren" },
      { season: "2023", driver: "M. Verstappen", constructorName: "Red Bull" },
    ],
    trackShape: "loop",
  },
] as const;

const CIRCUIT_BY_ID = new Map(SAMPLE_CIRCUITS.map((circuit) => [circuit.id, circuit]));

export function getSampleCircuit(id: string): CircuitProfile | undefined {
  return CIRCUIT_BY_ID.get(id);
}
