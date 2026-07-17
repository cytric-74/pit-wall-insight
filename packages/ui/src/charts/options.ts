import type { EChartsOption } from "echarts";

import { CHART_FONT_MONO, type ChartTheme } from "./theme.js";

const AXIS_LABEL_STYLE = (theme: ChartTheme) => ({
  color: theme.axisLabel,
  fontFamily: CHART_FONT_MONO,
  fontSize: 11,
});

/** Category (x) + value (y) axes for Line/Area/Bar charts. Grid stays subtle, axis stays neutral — never colored (docs/assets/06_CHART_DESIGN_SYSTEM.md). */
export function buildCategoryAxes(
  theme: ChartTheme,
  categories: readonly (string | number)[],
  xAxisLabel?: string,
  yAxisLabel?: string,
): Pick<EChartsOption, "xAxis" | "yAxis" | "grid"> {
  return {
    grid: { left: 48, right: 16, top: 24, bottom: 40, containLabel: true },
    xAxis: {
      type: "category",
      data: [...categories],
      ...(xAxisLabel !== undefined && { name: xAxisLabel, nameLocation: "middle", nameGap: 28 }),
      nameTextStyle: AXIS_LABEL_STYLE(theme),
      axisLine: { lineStyle: { color: theme.axis } },
      axisTick: { lineStyle: { color: theme.axis } },
      axisLabel: AXIS_LABEL_STYLE(theme),
      splitLine: { show: false },
    },
    yAxis: {
      type: "value",
      ...(yAxisLabel !== undefined && { name: yAxisLabel }),
      nameTextStyle: AXIS_LABEL_STYLE(theme),
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: AXIS_LABEL_STYLE(theme),
      splitLine: { lineStyle: { color: theme.grid, type: "dashed" } },
    },
  };
}

/** Numeric (value) x/y axes, for Scatter. */
export function buildValueAxes(
  theme: ChartTheme,
  xAxisLabel?: string,
  yAxisLabel?: string,
): Pick<EChartsOption, "xAxis" | "yAxis" | "grid"> {
  return {
    grid: { left: 48, right: 16, top: 24, bottom: 40, containLabel: true },
    xAxis: {
      type: "value",
      ...(xAxisLabel !== undefined && { name: xAxisLabel, nameLocation: "middle", nameGap: 28 }),
      nameTextStyle: AXIS_LABEL_STYLE(theme),
      axisLine: { lineStyle: { color: theme.axis } },
      axisTick: { lineStyle: { color: theme.axis } },
      axisLabel: AXIS_LABEL_STYLE(theme),
      splitLine: { lineStyle: { color: theme.grid, type: "dashed" } },
    },
    yAxis: {
      type: "value",
      ...(yAxisLabel !== undefined && { name: yAxisLabel }),
      nameTextStyle: AXIS_LABEL_STYLE(theme),
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: AXIS_LABEL_STYLE(theme),
      splitLine: { lineStyle: { color: theme.grid, type: "dashed" } },
    },
  };
}

/**
 * Tooltip + crosshair. `type: "cross"` is the "Telemetry Crosshair"
 * (docs/assets/07_CURSOR_SYSTEM.md): horizontal + vertical guide lines
 * meeting at the hovered point, with a coordinate label on each axis.
 */
export function buildTooltip(
  theme: ChartTheme,
  trigger: "axis" | "item",
  valueFormatter?: (value: number) => string,
): NonNullable<EChartsOption["tooltip"]> {
  return {
    trigger,
    backgroundColor: theme.tooltipBackground,
    borderColor: theme.tooltipBorder,
    borderWidth: 1,
    padding: [8, 12],
    textStyle: { color: theme.tooltipText, fontFamily: CHART_FONT_MONO, fontSize: 12 },
    extraCssText: "border-radius: 6px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);",
    ...(valueFormatter
      ? { valueFormatter: (value: unknown) => valueFormatter(Number(value)) }
      : {}),
    axisPointer: {
      type: "cross",
      lineStyle: { color: theme.crosshair, width: 1, type: "dashed" },
      crossStyle: { color: theme.crosshair, width: 1, type: "dashed" },
      label: {
        backgroundColor: theme.tooltipBackground,
        color: theme.tooltipText,
        fontFamily: CHART_FONT_MONO,
        borderColor: theme.tooltipBorder,
        borderWidth: 1,
      },
    },
  };
}

/** Understated legend, only rendered when there's more than one series (docs: "never dominate the chart"). */
export function buildLegend(theme: ChartTheme, seriesCount: number): EChartsOption["legend"] {
  if (seriesCount <= 1) return undefined;
  return {
    top: 0,
    right: 0,
    icon: "roundRect",
    itemWidth: 12,
    itemHeight: 3,
    textStyle: { color: theme.axisLabel, fontFamily: CHART_FONT_MONO, fontSize: 12 },
  };
}

/**
 * Series color priority (docs/assets/06_CHART_DESIGN_SYSTEM.md —
 * "Comparison Mode"): primary = constructor accent, secondary =
 * constructor secondary, anything beyond that = muted/historical rather
 * than introducing more accent colors ("never rainbow palettes").
 */
export function seriesColor(theme: ChartTheme, index: number, override?: string): string {
  if (override) return override;
  if (index === 0) return theme.primary;
  if (index === 1) return theme.secondary;
  return theme.historical;
}
