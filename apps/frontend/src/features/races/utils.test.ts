import { describe, expect, it } from "vitest";

import { buildPositionSeries, buildStrategyEvents, estimateRaceLaps } from "./utils.js";

describe("buildPositionSeries", () => {
  it("aligns every driver's series to laps every driver has a position for", () => {
    const chart = buildPositionSeries([
      { driver: "Max Verstappen", lapNumber: 1, position: 1 },
      { driver: "Max Verstappen", lapNumber: 2, position: 1 },
      { driver: "Charles Leclerc", lapNumber: 1, position: 2 },
      { driver: "Charles Leclerc", lapNumber: 2, position: 2 },
      // Leclerc has no lap 3 recorded, so lap 3 must be excluded entirely,
      // even though Verstappen does have one.
      { driver: "Max Verstappen", lapNumber: 3, position: 1 },
    ]);

    expect(chart.categories).toEqual([1, 2]);
    expect(chart.series).toEqual([
      { driver: "Max Verstappen", data: [1, 1] },
      { driver: "Charles Leclerc", data: [2, 2] },
    ]);
  });

  it("drops laps with a null position rather than fabricating a value", () => {
    const chart = buildPositionSeries([
      { driver: "Max Verstappen", lapNumber: 1, position: 1 },
      { driver: "Max Verstappen", lapNumber: 2, position: null },
    ]);

    expect(chart.categories).toEqual([1]);
    expect(chart.series).toEqual([{ driver: "Max Verstappen", data: [1] }]);
  });

  it("returns an empty chart for no positions at all", () => {
    expect(buildPositionSeries([])).toEqual({ categories: [], series: [] });
  });
});

describe("estimateRaceLaps", () => {
  it("returns the highest lap number seen across every driver", () => {
    const laps = estimateRaceLaps([
      { driver: "Max Verstappen", lapNumber: 3, position: 1 },
      { driver: "Charles Leclerc", lapNumber: 5, position: 2 },
    ]);

    expect(laps).toBe(5);
  });

  it("returns undefined when there is no position data yet", () => {
    expect(estimateRaceLaps([])).toBeUndefined();
  });
});

describe("buildStrategyEvents", () => {
  it("emits one event per stint change, after the first stint, in lap order", () => {
    const events = buildStrategyEvents([
      {
        driver: "Max Verstappen",
        stints: [
          { compound: "SOFT", startLap: 1, endLap: 10, lapCount: 10 },
          { compound: "HARD", startLap: 11, endLap: 20, lapCount: 10 },
        ],
      },
      {
        driver: "Charles Leclerc",
        stints: [{ compound: "MEDIUM", startLap: 1, endLap: 20, lapCount: 20 }],
      },
    ]);

    // Leclerc never changed compound, so he contributes zero events —
    // only Verstappen's single switch shows up.
    expect(events).toEqual([{ lap: 11, label: "Max Verstappen switches to HARD tyres" }]);
  });

  it("labels an unknown compound honestly rather than omitting it", () => {
    const events = buildStrategyEvents([
      {
        driver: "Max Verstappen",
        stints: [
          { compound: "SOFT", startLap: 1, endLap: 10, lapCount: 10 },
          { compound: null, startLap: 11, endLap: 20, lapCount: 10 },
        ],
      },
    ]);

    expect(events).toEqual([
      { lap: 11, label: "Max Verstappen switches to unknown compound tyres" },
    ]);
  });

  it("returns no events for a driver with only one stint", () => {
    const events = buildStrategyEvents([
      {
        driver: "Max Verstappen",
        stints: [{ compound: "SOFT", startLap: 1, endLap: 20, lapCount: 20 }],
      },
    ]);

    expect(events).toEqual([]);
  });
});
