import type { EChartsOption } from "echarts";
import { useMemo } from "react";

import { EChart } from "./EChart.js";
import { buildTooltip, buildValueAxes, seriesColor } from "./options.js";
import { useChartTheme } from "./theme.js";

export interface ScatterSeriesData {
  name: string;
  /** `[x, y]` pairs — numeric on both axes, unlike the category-axis charts. */
  data: readonly (readonly [number, number])[];
  color?: string;
}

export interface ScatterChartProps {
  series: readonly ScatterSeriesData[];
  height?: number | string;
  loading?: boolean;
  className?: string;
  ariaLabel?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  valueFormatter?: (value: number) => string;
  /** "Small markers. Engineering precision. Never oversized circles." Defaults to 8. */
  symbolSize?: number;
}

/**
 * "Scatter Charts: small markers, engineering precision, never oversized
 * circles." (docs/assets/06_CHART_DESIGN_SYSTEM.md)
 */
export function ScatterChart({
  series,
  height = 320,
  loading = false,
  className,
  ariaLabel,
  xAxisLabel,
  yAxisLabel,
  valueFormatter,
  symbolSize = 8,
}: ScatterChartProps) {
  const theme = useChartTheme();

  const option = useMemo<EChartsOption>(
    () => ({
      ...buildValueAxes(theme, xAxisLabel, yAxisLabel),
      tooltip: buildTooltip(theme, "item", valueFormatter),
      series: series.map((item, index) => ({
        name: item.name,
        type: "scatter" as const,
        data: item.data.map(([x, y]) => [x, y]),
        symbolSize,
        itemStyle: { color: seriesColor(theme, index, item.color) },
      })),
    }),
    [theme, series, xAxisLabel, yAxisLabel, valueFormatter, symbolSize],
  );

  return (
    <EChart
      option={option}
      height={height}
      loading={loading}
      ariaLabel={ariaLabel ?? "Scatter plot"}
      {...(className !== undefined && { className })}
    />
  );
}
