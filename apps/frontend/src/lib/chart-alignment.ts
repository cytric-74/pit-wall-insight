export interface AlignedSeries {
  key: string;
  data: number[];
}

export interface AlignedChart {
  categories: number[];
  series: AlignedSeries[];
}

/**
 * Groups `items` by `getGroupKey`, then aligns every group to the
 * intersection of category values every group has data for — a chart's
 * series must all share one `categories` axis, and not every group
 * necessarily has data for every category (e.g. tyre compounds run for
 * different numbers of laps, a driver may be missing a recorded lap).
 * Previously implemented three separate times with near-identical logic
 * (`buildPositionSeries`, `buildDegradationSeries`, and part of
 * `buildPaceSeries`) with no shared test coverage protecting any of them
 * (Phase 7 audit, Medium) — this is the one copy all three now call.
 */
export function alignSeriesByCategory<T>(
  items: readonly T[],
  getGroupKey: (item: T) => string,
  getCategory: (item: T) => number,
  getValue: (item: T) => number,
): AlignedChart {
  const byGroup = new Map<string, Map<number, number>>();
  for (const item of items) {
    const key = getGroupKey(item);
    const values = byGroup.get(key) ?? new Map<number, number>();
    values.set(getCategory(item), getValue(item));
    byGroup.set(key, values);
  }

  const allCategories = [...new Set(items.map(getCategory))].sort((a, b) => a - b);
  const categories = allCategories.filter((category) =>
    [...byGroup.values()].every((values) => values.has(category)),
  );

  return {
    categories,
    series: [...byGroup.entries()].map(([key, values]) => ({
      key,
      data: categories.map((category) => values.get(category)!),
    })),
  };
}
