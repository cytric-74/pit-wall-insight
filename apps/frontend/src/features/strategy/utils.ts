import type { TyreDegradationPoint } from "@pit-wall-insight/shared-types";

export interface DegradationSeries {
  compound: string;
  data: number[];
}

export interface DegradationChart {
  categories: number[];
  series: DegradationSeries[];
}

/** Groups `GET /strategy/tyres` points into one series per compound,
 * aligned to the tyre-life values every present compound has data for —
 * same intersection approach as `features/drivers/utils.ts::buildPaceSeries`,
 * since a chart's series must all share one `categories` axis and
 * compounds don't necessarily run for the same number of laps. */
export function buildDegradationSeries(points: readonly TyreDegradationPoint[]): DegradationChart {
  const byCompound = new Map<string, Map<number, number>>();
  for (const point of points) {
    const values = byCompound.get(point.compound) ?? new Map<number, number>();
    values.set(point.tyreLife, point.averageLapTime);
    byCompound.set(point.compound, values);
  }

  const tyreLifeValues = [...new Set(points.map((point) => point.tyreLife))].sort((a, b) => a - b);
  const categories = tyreLifeValues.filter((life) =>
    [...byCompound.values()].every((values) => values.has(life)),
  );

  return {
    categories,
    series: [...byCompound.entries()].map(([compound, values]) => ({
      compound,
      data: categories.map((life) => values.get(life)!),
    })),
  };
}

export interface CompoundEffectiveness {
  compound: string;
  averageLapTime: number;
}

/** Average lap time per compound, weighted by how many laps each
 * (compound, tyreLife) point was averaged from — a real aggregate over
 * `GET /strategy/tyres`, not a separate model. */
export function computeCompoundEffectiveness(
  points: readonly TyreDegradationPoint[],
): CompoundEffectiveness[] {
  const totals = new Map<string, { weightedSum: number; sampleCount: number }>();
  for (const point of points) {
    const entry = totals.get(point.compound) ?? { weightedSum: 0, sampleCount: 0 };
    entry.weightedSum += point.averageLapTime * point.sampleCount;
    entry.sampleCount += point.sampleCount;
    totals.set(point.compound, entry);
  }

  return [...totals.entries()]
    .map(([compound, { weightedSum, sampleCount }]) => ({
      compound,
      averageLapTime: weightedSum / sampleCount,
    }))
    .sort((a, b) => a.averageLapTime - b.averageLapTime);
}

export type CompoundBadgeVariant = "danger" | "warning" | "neutral" | "info";

const BADGE_VARIANT_BY_COMPOUND: Readonly<Record<string, CompoundBadgeVariant>> = {
  SOFT: "danger",
  MEDIUM: "warning",
  HARD: "neutral",
  INTERMEDIATE: "info",
  WET: "info",
};

/** Real compound values (`SOFT`/`MEDIUM`/`HARD`/`INTERMEDIATE`/`WET`) to a
 * `Badge` variant, matching real tyre compound coloring (soft = red,
 * medium = yellow, hard = white, wet-weather = blue) the same way the
 * sample-data version did — falls back to `neutral` for anything
 * unrecognized rather than throwing on a missing key. */
export function resolveCompoundBadgeVariant(compound: string | null): CompoundBadgeVariant {
  if (!compound) return "neutral";
  return BADGE_VARIANT_BY_COMPOUND[compound.toUpperCase()] ?? "neutral";
}
