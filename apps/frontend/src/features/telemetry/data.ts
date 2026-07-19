import type { ConstructorId } from "@pit-wall-insight/ui";

/**
 * SAMPLE DATA — hand-written placeholder values, not a real telemetry
 * capture. The page shows a visible "Sample data" badge for the same
 * reason. Replace this module with a TanStack Query hook against
 * `/api/v1/telemetry/...` (`fct_telemetry`, 100ms samples of speed, rpm,
 * gear, throttle, brake, drs, x/y/z per docs/07_DATABASE_SCHEMA.md) once
 * the backend exists — the page consumes only the `TelemetrySession`
 * shape, so swapping the source should not touch the components.
 */

export interface TelemetryTrace {
  driver: string;
  abbreviation: string;
  constructorId: ConstructorId;
  speed: readonly number[];
  throttle: readonly number[];
  brake: readonly number[];
  rpm: readonly number[];
  gear: readonly number[];
}

export interface SectorTime {
  sector: string;
  times: Readonly<Record<string, number>>;
}

export interface TelemetrySession {
  id: string;
  sessionName: string;
  circuit: string;
  lapNumber: number;
  compound: string;
  summary: {
    topSpeed: number;
    averageThrottle: number;
    averageBrake: number;
    topRpm: number;
  };
  drivers: readonly [TelemetryTrace, TelemetryTrace];
  sectors: readonly SectorTime[];
}

export const DISTANCE_MARKERS: readonly string[] = [
  "0m",
  "300m",
  "600m",
  "900m",
  "1200m",
  "1500m",
  "1800m",
  "2100m",
  "2400m",
  "2700m",
];

export const SAMPLE_TELEMETRY_SESSIONS: readonly TelemetrySession[] = [
  {
    id: "bahrain-q3",
    sessionName: "Qualifying — Q3",
    circuit: "Bahrain International Circuit",
    lapNumber: 14,
    compound: "Soft",
    summary: { topSpeed: 322, averageThrottle: 61, averageBrake: 18, topRpm: 11800 },
    drivers: [
      {
        driver: "Verstappen",
        abbreviation: "VER",
        constructorId: "red-bull",
        speed: [80, 210, 305, 322, 140, 260, 300, 190, 250, 310],
        throttle: [40, 90, 100, 100, 20, 85, 100, 35, 80, 100],
        brake: [0, 0, 0, 0, 95, 5, 0, 90, 0, 0],
        rpm: [9200, 10800, 11600, 11800, 8600, 10600, 11700, 9000, 10500, 11750],
        gear: [3, 6, 8, 8, 2, 6, 8, 3, 6, 8],
      },
      {
        driver: "Norris",
        abbreviation: "NOR",
        constructorId: "mclaren",
        speed: [78, 205, 300, 318, 145, 255, 296, 195, 248, 305],
        throttle: [38, 88, 100, 100, 25, 82, 100, 40, 78, 100],
        brake: [0, 0, 0, 0, 90, 8, 0, 85, 0, 0],
        rpm: [9100, 10700, 11500, 11750, 8700, 10500, 11650, 9100, 10450, 11700],
        gear: [3, 6, 8, 8, 2, 6, 8, 3, 6, 8],
      },
    ],
    sectors: [
      { sector: "Sector 1", times: { VER: 28.412, NOR: 28.501 } },
      { sector: "Sector 2", times: { VER: 39.87, NOR: 39.71 } },
      { sector: "Sector 3", times: { VER: 24.165, NOR: 24.23 } },
    ],
  },
  {
    id: "monaco-q3",
    sessionName: "Qualifying — Q3",
    circuit: "Circuit de Monaco",
    lapNumber: 18,
    compound: "Soft",
    summary: { topSpeed: 288, averageThrottle: 52, averageBrake: 24, topRpm: 11400 },
    drivers: [
      {
        driver: "Leclerc",
        abbreviation: "LEC",
        constructorId: "ferrari",
        speed: [60, 180, 260, 288, 90, 200, 270, 110, 190, 265],
        throttle: [30, 80, 100, 100, 15, 75, 100, 20, 70, 95],
        brake: [0, 0, 0, 0, 98, 10, 0, 96, 5, 0],
        rpm: [8600, 10200, 11200, 11400, 8000, 10000, 11300, 8200, 9900, 11250],
        gear: [2, 5, 7, 7, 1, 5, 7, 2, 5, 7],
      },
      {
        driver: "Verstappen",
        abbreviation: "VER",
        constructorId: "red-bull",
        speed: [58, 176, 255, 282, 92, 196, 264, 112, 186, 260],
        throttle: [28, 78, 100, 100, 18, 74, 100, 22, 68, 94],
        brake: [0, 0, 0, 0, 95, 12, 0, 94, 6, 0],
        rpm: [8500, 10100, 11100, 11300, 8100, 9950, 11250, 8250, 9850, 11200],
        gear: [2, 5, 7, 7, 1, 5, 7, 2, 5, 7],
      },
    ],
    sectors: [
      { sector: "Sector 1", times: { LEC: 18.221, VER: 18.304 } },
      { sector: "Sector 2", times: { LEC: 31.05, VER: 30.98 } },
      { sector: "Sector 3", times: { LEC: 23.638, VER: 23.702 } },
    ],
  },
  {
    id: "silverstone-q3",
    sessionName: "Qualifying — Q3",
    circuit: "Silverstone Circuit",
    lapNumber: 16,
    compound: "Soft",
    summary: { topSpeed: 331, averageThrottle: 66, averageBrake: 15, topRpm: 11900 },
    drivers: [
      {
        driver: "Norris",
        abbreviation: "NOR",
        constructorId: "mclaren",
        speed: [95, 225, 315, 331, 160, 275, 310, 205, 265, 320],
        throttle: [45, 92, 100, 100, 28, 88, 100, 42, 84, 100],
        brake: [0, 0, 0, 0, 88, 4, 0, 82, 0, 0],
        rpm: [9400, 10900, 11700, 11900, 8800, 10700, 11800, 9200, 10600, 11850],
        gear: [3, 6, 8, 8, 2, 6, 8, 4, 6, 8],
      },
      {
        driver: "Verstappen",
        abbreviation: "VER",
        constructorId: "red-bull",
        speed: [93, 220, 310, 326, 165, 270, 305, 210, 260, 316],
        throttle: [43, 90, 100, 100, 30, 86, 100, 44, 82, 100],
        brake: [0, 0, 0, 0, 85, 6, 0, 80, 0, 0],
        rpm: [9300, 10800, 11650, 11850, 8850, 10650, 11750, 9250, 10550, 11800],
        gear: [3, 6, 8, 8, 2, 6, 8, 4, 6, 8],
      },
    ],
    sectors: [
      { sector: "Sector 1", times: { NOR: 26.804, VER: 26.85 } },
      { sector: "Sector 2", times: { NOR: 35.12, VER: 35.29 } },
      { sector: "Sector 3", times: { NOR: 22.41, VER: 22.39 } },
    ],
  },
] as const;

const SESSION_BY_ID = new Map(SAMPLE_TELEMETRY_SESSIONS.map((session) => [session.id, session]));

export function getSampleSession(id: string): TelemetrySession | undefined {
  return SESSION_BY_ID.get(id);
}
