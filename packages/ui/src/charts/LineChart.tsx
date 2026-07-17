import type { EChartsOption } from "echarts";
import { useMemo } from "react";

import { EChart } from "./EChart.js";
import { buildCategoryAxes, buildLegend, buildTooltip, seriesColor } from "./options.js";
import { useChartTheme } from "./theme.js";

export interface CategorySeriesData {
  name: string;
  data: readonly number[];
  /** Overrides the default primary/secondary/historical color sequence. */
  color?: string;
}

export interface CategoryChartProps {
  categories: readonly (string | number)[];
  series: readonly CategorySeriesData[];
  height?: number | string;
  loading?: boolean;
  className?: string;
  ariaLabel?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  valueFormatter?: (value: number) => string;
}

export interface LineChartProps extends CategoryChartProps {
  /** Respect the data's actual shape rather than exaggerating it (docs: "avoid exaggerated smoothing"). Defaults to false. */
  smooth?: boolean;
}

/**
 * The signature visualization (docs/assets/06_CHART_DESIGN_SYSTEM.md —
 * "Line Charts: the signature visualization. Should resemble telemetry
 * traces."). Data points stay hidden until hovered
 * ("Data Points: Hidden by default. Appear only on interaction").
 */
export function LineChart({
  categories,
  series,
  height = 320,
  loading = false,
  className,
  ariaLabel,
  xAxisLabel,
  yAxisLabel,
  valueFormatter,
  smooth = false,
}: LineChartProps) {
  const theme = useChartTheme();

  const legend = buildLegend(theme, series.length);

  const option = useMemo<EChartsOption>(
    () => ({
      ...buildCategoryAxes(theme, categories, xAxisLabel, yAxisLabel),
      ...(legend !== undefined && { legend }),
      tooltip: buildTooltip(theme, "axis", valueFormatter),
      series: series.map((item, index) => ({
        name: item.name,
        type: "line" as const,
        data: [...item.data],
        smooth,
        showSymbol: false,
        symbolSize: 6,
        lineStyle: { width: index === 0 ? 3 : 2, color: seriesColor(theme, index, item.color) },
        itemStyle: { color: seriesColor(theme, index, item.color) },
        emphasis: { focus: "series" as const },
      })),
    }),
    [theme, categories, series, xAxisLabel, yAxisLabel, valueFormatter, smooth, legend],
  );

  return (
    <EChart
      option={option}
      height={height}
      loading={loading}
      ariaLabel={ariaLabel ?? "Line chart"}
      {...(className !== undefined && { className })}
    />
  );
}
