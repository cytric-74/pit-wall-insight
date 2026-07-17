import type { EChartsOption } from "echarts";
import { useMemo } from "react";

import { EChart } from "./EChart.js";
import type { CategoryChartProps } from "./LineChart.js";
import { buildCategoryAxes, buildLegend, buildTooltip, seriesColor } from "./options.js";
import { useChartTheme } from "./theme.js";

/**
 * "Bar Charts: Sharp corners. Minimal radius. Consistent spacing. No
 * gradients. Hover brightens only." (docs/assets/06_CHART_DESIGN_SYSTEM.md)
 */
export function BarChart({
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
      series: series.map((item, index) => ({
        name: item.name,
        type: "bar" as const,
        data: [...item.data],
        barGap: "20%",
        barMaxWidth: 32,
        itemStyle: { color: seriesColor(theme, index, item.color), borderRadius: [2, 2, 0, 0] },
        emphasis: { itemStyle: { opacity: 0.85 } },
      })),
    }),
    [theme, categories, series, xAxisLabel, yAxisLabel, valueFormatter, legend],
  );

  return (
    <EChart
      option={option}
      height={height}
      loading={loading}
      ariaLabel={ariaLabel ?? "Bar chart"}
      {...(className !== undefined && { className })}
    />
  );
}
