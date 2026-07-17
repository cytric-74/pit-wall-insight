/**
 * Chart components (docs/assets/06_CHART_DESIGN_SYSTEM.md) — first-class
 * UI backed by Apache ECharts, never instantiated ad hoc inside pages.
 *
 * Implemented: LineChart, AreaChart, BarChart, ScatterChart. Not yet
 * implemented: RadarChart, Heatmap, TelemetryChart, SectorComparisonChart,
 * and the other domain-specific chart compositions named in
 * docs/09_COMPONENT_LIBRARY.md.
 */

export * from "./AreaChart.js";
export * from "./BarChart.js";
export * from "./LineChart.js";
export * from "./ScatterChart.js";
export * from "./theme.js";
