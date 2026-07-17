import { BarChart, LineChart, ScatterChart } from "echarts/charts";
import {
  DatasetComponent,
  GridComponent,
  LegendComponent,
  TooltipComponent,
} from "echarts/components";
import * as echarts from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";

/**
 * Modular ECharts registration — only the chart types and components this
 * system actually uses (Line/Bar/Scatter, Grid/Tooltip/Legend/Dataset,
 * Canvas renderer), rather than importing the full `echarts` bundle.
 * Area charts reuse LineChart with `areaStyle` set; there's no separate
 * "area" chart type in ECharts.
 */
echarts.use([
  LineChart,
  BarChart,
  ScatterChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DatasetComponent,
  CanvasRenderer,
]);

export { echarts };
