import { describe, expect, it } from "vitest";

import {
  buildDegradationSeries,
  computeCompoundEffectiveness,
  resolveCompoundBadgeVariant,
} from "./utils.js";

describe("buildDegradationSeries", () => {
  it("aligns every compound to the tyre-life values every compound has data for", () => {
    const chart = buildDegradationSeries([
      { compound: "SOFT", tyreLife: 1, averageLapTime: 90.0, sampleCount: 5 },
      { compound: "SOFT", tyreLife: 2, averageLapTime: 90.5, sampleCount: 5 },
      { compound: "HARD", tyreLife: 1, averageLapTime: 91.0, sampleCount: 5 },
      // HARD has no tyreLife=2 point, so tyreLife=2 must be excluded
      // entirely, even though SOFT does have one.
    ]);

    expect(chart.categories).toEqual([1]);
    expect(chart.series).toEqual([
      { compound: "SOFT", data: [90.0] },
      { compound: "HARD", data: [91.0] },
    ]);
  });

  it("returns an empty chart for no points at all", () => {
    expect(buildDegradationSeries([])).toEqual({ categories: [], series: [] });
  });
});

describe("computeCompoundEffectiveness", () => {
  it("weights each compound's average by sample count and sorts fastest first", () => {
    const effectiveness = computeCompoundEffectiveness([
      { compound: "HARD", tyreLife: 1, averageLapTime: 92.0, sampleCount: 1 },
      { compound: "SOFT", tyreLife: 1, averageLapTime: 90.0, sampleCount: 3 },
      { compound: "SOFT", tyreLife: 2, averageLapTime: 91.0, sampleCount: 1 },
    ]);

    // SOFT: (90*3 + 91*1) / 4 = 90.25
    expect(effectiveness).toEqual([
      { compound: "SOFT", averageLapTime: 90.25 },
      { compound: "HARD", averageLapTime: 92.0 },
    ]);
  });

  it("returns an empty list for no points at all", () => {
    expect(computeCompoundEffectiveness([])).toEqual([]);
  });
});

describe("resolveCompoundBadgeVariant", () => {
  it.each([
    ["SOFT", "danger"],
    ["MEDIUM", "warning"],
    ["HARD", "neutral"],
    ["INTERMEDIATE", "info"],
    ["WET", "info"],
  ] as const)("maps %s to %s", (compound, variant) => {
    expect(resolveCompoundBadgeVariant(compound)).toBe(variant);
  });

  it("is case-insensitive", () => {
    expect(resolveCompoundBadgeVariant("soft")).toBe("danger");
  });

  it("falls back to neutral for an unrecognized compound", () => {
    expect(resolveCompoundBadgeVariant("SUPERSOFT")).toBe("neutral");
  });

  it("falls back to neutral for null", () => {
    expect(resolveCompoundBadgeVariant(null)).toBe("neutral");
  });
});
