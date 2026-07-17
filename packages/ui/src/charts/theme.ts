import { useMemo } from "react";

import { useConstructorTheme } from "../theme/theme-provider.js";

/**
 * ECharts renders to `<canvas>`, so it can't read CSS custom properties —
 * these values are the same ones defined in
 * packages/config/tailwind/tokens.css, duplicated here on purpose (the
 * same accepted tradeoff as constructor-themes.css / constructors.ts: a
 * change to the neutral palette or a team's colors must be mirrored here).
 */
const NEUTRAL_CHART_COLORS = {
  surfaceElevated: "#181818",
  borderDefault: "#2b2b2b",
  borderSubtle: "rgba(255, 255, 255, 0.08)",
  textPrimary: "#ffffff",
  textMuted: "#8d8d8d",
  success: "#00c853",
  warning: "#ffc107",
  danger: "#e53935",
  info: "#00b0ff",
} as const;

/** Default accent (tokens.css `--color-accent-*`) — used before any constructor is selected. */
const DEFAULT_ACCENT = {
  primary: "#ff1801",
  secondary: "#ff5a3d",
} as const;

export const CHART_FONT_MONO = '"IBM Plex Mono", ui-monospace, "SFMono-Regular", monospace';
export const CHART_FONT_DISPLAY = '"Space Grotesk", ui-sans-serif, system-ui, sans-serif';

export interface ChartTheme {
  /** Primary series color — the active constructor's accent, or the default accent. */
  primary: string;
  /** Secondary series color. */
  secondary: string;
  /** Gridline color. */
  grid: string;
  /** Axis line/tick color. */
  axis: string;
  /** Axis/legend label color. */
  axisLabel: string;
  tooltipBackground: string;
  tooltipBorder: string;
  tooltipText: string;
  /** Crosshair / axis-pointer color — matches the active accent. */
  crosshair: string;
  success: string;
  warning: string;
  danger: string;
  info: string;
  /** Muted color for historical/reference series (docs/assets/06_CHART_DESIGN_SYSTEM.md — "Comparison Mode"). */
  historical: string;
}

/**
 * Bridges the constructor theme (packages/ui/src/theme) into chart colors.
 * Only the accent changes with the constructor — grid/axis/tooltip stay
 * neutral, matching "Constructor Themes... Grid remains unchanged. Axis
 * remains unchanged. Layout remains unchanged."
 */
export function useChartTheme(): ChartTheme {
  const { constructor } = useConstructorTheme();

  return useMemo<ChartTheme>(() => {
    const primary = constructor?.primary ?? DEFAULT_ACCENT.primary;
    const secondary = constructor?.secondary ?? DEFAULT_ACCENT.secondary;

    return {
      primary,
      secondary,
      grid: NEUTRAL_CHART_COLORS.borderSubtle,
      axis: NEUTRAL_CHART_COLORS.borderDefault,
      axisLabel: NEUTRAL_CHART_COLORS.textMuted,
      tooltipBackground: NEUTRAL_CHART_COLORS.surfaceElevated,
      tooltipBorder: NEUTRAL_CHART_COLORS.borderDefault,
      tooltipText: NEUTRAL_CHART_COLORS.textPrimary,
      crosshair: primary,
      success: NEUTRAL_CHART_COLORS.success,
      warning: NEUTRAL_CHART_COLORS.warning,
      danger: NEUTRAL_CHART_COLORS.danger,
      info: NEUTRAL_CHART_COLORS.info,
      historical: NEUTRAL_CHART_COLORS.textMuted,
    };
  }, [constructor?.primary, constructor?.secondary]);
}
