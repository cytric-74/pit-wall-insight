import type { EChartsOption } from "echarts";
import { useMemo } from "react";

import { hexToRgba } from "./color.js";
import { EChart } from "./EChart.js";
import type { CategoryChartProps } from "./LineChart.js";
import { buildCategoryAxes, buildLegend, buildTooltip, seriesColor } from "./options.js";
import { useChartTheme } from "./theme.js";

/**
 * "Area Charts: Use sparingly. Only when emphasizing magnitude. Opacity
 * remains low... Gradient. Always." (docs/assets/06_CHART_DESIGN_SYSTEM.md)
 * A `LineChart` with a low-opacity gradient fill under the line, rather
 * than a distinct chart type — ECharts itself has no separate "area"
 * series, just `areaStyle` on a line series.
 */
export function AreaChart({
  categories,
  series,
  height = 320,
  loading = false,
  className,
  ariaLabel,
  xAxisLabel,
  yAxisLabel,
  valueFormatter,
}: CategoryChartProps) {
  const theme = useChartTheme();
  const legend = buildLegend(theme, series.length);

  const option = useMemo<EChartsOption>(
    () => ({
      ...buildCategoryAxes(theme, categories, xAxisLabel, yAxisLabel),
      ...(legend !== undefined && { legend }),
      tooltip: buildTooltip(theme, "axis", valueFormatter),
      series: series.map((item, index) => {
        const color = seriesColor(theme, index, item.color);
        return {
          name: item.name,
          type: "line" as const,
          data: [...item.data],
          showSymbol: false,
          symbolSize: 6,
          lineStyle: { width: index === 0 ? 3 : 2, color },
          itemStyle: { color },
          areaStyle: {
            color: {
              type: "linear" as const,
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: hexToRgba(color, 0.28) },
                { offset: 1, color: hexToRgba(color, 0) },
              ],
            },
          },
          emphasis: { focus: "series" as const },
        };
      }),
    }),
    [theme, categories, series, xAxisLabel, yAxisLabel, valueFormatter, legend],
  );

  return (
    <EChart
      option={option}
      height={height}
      loading={loading}
      ariaLabel={ariaLabel ?? "Area chart"}
      {...(className !== undefined && { className })}
    />
  );
}
