import type { DriverStrategy, PositionEntry } from "@pit-wall-insight/shared-types";

import { alignSeriesByCategory } from "../../lib/chart-alignment.js";

export interface DriverPositionSeries {
  driver: string;
  data: number[];
}

export interface PositionChart {
  categories: number[];
  series: DriverPositionSeries[];
}

/** Groups `GET /races/{id}/positions` (one row per driver per lap) into
 * one series per driver, aligned to the shared set of lap numbers that
 * appear across all of them — a chart's series must all share one
 * `categories` axis. Laps with a `null` position are dropped per driver
 * rather than coerced to a fabricated number. */
export function buildPositionSeries(positions: readonly PositionEntry[]): PositionChart {
  const withPosition = positions.filter(
    (entry): entry is PositionEntry & { position: number } => entry.position !== null,
  );
  const aligned = alignSeriesByCategory(
    withPosition,
    (entry) => entry.driver,
    (entry) => entry.lapNumber,
    (entry) => entry.position,
  );

  return {
    categories: aligned.categories,
    series: aligned.series.map((series) => ({ driver: series.key, data: series.data })),
  };
}

/** This race's total lap count, approximated as the highest lap number any
 * driver reached — `RaceSummary` has no `laps` field (no single "race
 * distance" value is tracked anywhere), so this is derived from the same
 * per-lap position data the "Position changes" chart already uses. */
export function estimateRaceLaps(positions: readonly PositionEntry[]): number | undefined {
  if (positions.length === 0) return undefined;
  return Math.max(...positions.map((entry) => entry.lapNumber));
}

export interface StrategyEvent {
  lap: number;
  label: string;
}

/** Reinterprets tyre-stint changes (`GET /races/{id}/strategy`) as a race
 * timeline — there's no real event log in this pipeline (no safety car/VSC
 * data is collected anywhere), so "race events" here means "tyre changes",
 * honestly labeled as such, across every driver, in lap order. */
export function buildStrategyEvents(strategies: readonly DriverStrategy[]): StrategyEvent[] {
  const events: StrategyEvent[] = [];
  for (const strategy of strategies) {
    for (let index = 1; index < strategy.stints.length; index += 1) {
      const stint = strategy.stints[index]!;
      events.push({
        lap: stint.startLap,
        label: `${strategy.driver} switches to ${stint.compound ?? "unknown compound"} tyres`,
      });
    }
  }
  return events.sort((a, b) => a.lap - b.lap);
}
