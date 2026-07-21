import type { EChartsOption } from "echarts";
import { useReducedMotion } from "framer-motion";
import { useEffect, useRef } from "react";

import { cn } from "../lib/cn.js";
import { Skeleton } from "../loading/Skeleton.js";
import { echarts } from "./setup.js";

export interface EChartProps {
  option: EChartsOption;
  height?: number | string;
  /** Shows a skeleton overlay instead of the chart — for data not wired up yet. */
  loading?: boolean;
  className?: string;
  /** Accessible name — a canvas has no text content of its own. */
  ariaLabel?: string;
}

/**
 * Low-level ECharts lifecycle wrapper (init/resize/dispose). The four
 * public chart components (Line/Bar/Scatter/Area) build the `option`
 * object and render this — nothing outside charts/ should use it
 * directly.
 *
 * Responsive via `ResizeObserver` on the container (not a window resize
 * listener), so the chart also reflows when the sidebar collapses/expands
 * or any other layout change resizes its container without the viewport
 * itself changing.
 */
export function EChart({
  option,
  height = 320,
  loading = false,
  className,
  ariaLabel,
}: EChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<echarts.ECharts | null>(null);
  const prefersReducedMotion = useReducedMotion();

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const chart = echarts.init(container);
    chartRef.current = chart;

    const resizeObserver = new ResizeObserver(() => {
      chart.resize();
    });
    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
      chart.dispose();
      chartRef.current = null;
    };
  }, []);

  useEffect(() => {
    chartRef.current?.setOption(
      { animation: !prefersReducedMotion, ...option },
      { notMerge: true },
    );
  }, [option, prefersReducedMotion]);

  return (
    <div style={{ height }} data-cursor="chart" className={cn("relative w-full", className)}>
      <div ref={containerRef} role="img" aria-label={ariaLabel} className="h-full w-full" />
      {loading ? (
        <div className="absolute inset-0">
          <Skeleton className="h-full w-full" />
        </div>
      ) : null}
    </div>
  );
}
