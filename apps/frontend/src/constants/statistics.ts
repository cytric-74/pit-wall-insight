import type { StatisticsItem } from "@pit-wall-insight/ui";

/**
 * Mission Control's Statistics section. Placeholder season figures — not
 * wired to real data yet (out of scope for this task).
 */
export const STATISTICS: readonly StatisticsItem[] = [
  {
    label: "Races completed",
    value: 24,
    trend: { direction: "up", value: "+4%" },
    description: "Full calendar completed this season.",
  },
  {
    label: "Podium finishes",
    value: 72,
    trend: { direction: "up", value: "+8%" },
    description: "Across every constructor this season.",
  },
  {
    label: "Avg. pit stop",
    value: 2.3,
    unit: "s",
    precision: 1,
    // A faster average is the good outcome here, so a "down" trend still
    // reads as positive — see StatCardTrend.sentiment.
    trend: { direction: "down", value: "-0.4s", sentiment: "positive" },
    description: "Fastest average across the grid.",
  },
  {
    label: "Overtakes recorded",
    value: 1284,
    trend: { direction: "up", value: "+12%" },
    description: "Total on-track position changes.",
  },
] as const;
