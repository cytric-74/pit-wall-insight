import { motion, useReducedMotion } from "framer-motion";
import { TrendingDown, TrendingUp } from "lucide-react";

import { cn } from "../lib/cn.js";
import { EASE_STANDARD, useCountUp } from "../lib/motion.js";
import { Surface } from "../ui/Surface.js";

const MotionSurface = motion.create(Surface);

export interface StatCardTrend {
  /** Controls only the arrow glyph. */
  direction: "up" | "down";
  /** Pre-formatted, e.g. "+12%" — include the sign so meaning never depends on color/arrow alone. */
  value: string;
  /**
   * Controls color. Defaults to matching `direction` (up=positive,
   * down=negative) — override for metrics where a decrease is the good
   * outcome (e.g. pit stop time, lap time).
   */
  sentiment?: "positive" | "negative";
}

export interface StatCardProps {
  label: string;
  value: number;
  unit?: string;
  /** Decimal places for both the animated and final value. Defaults to 0. */
  precision?: number;
  trend?: StatCardTrend;
  description?: string;
  /** Count-up duration in seconds. Defaults to 1.2. */
  duration?: number;
  className?: string;
}

/**
 * "KPI Panel: Label -> Value -> Unit -> Delta -> Supporting Context. The
 * number is always the hero." (docs/assets/09_COMPONENT_STYLING.md)
 *
 * The value counts up from 0 once scrolled into view
 * (docs/10_ANIMATION_AND_INTERACTIONS.md — "Numbers: every important
 * metric animates... uses easing, never linear") and fades in alongside
 * it — one `useInView` observer drives both. Reduced motion shows the
 * final value immediately with no animation.
 *
 * Screen readers get the final value right away regardless of animation
 * progress: the visible, animating number is `aria-hidden`, backed by a
 * `sr-only` summary that includes the trend and description too.
 */
export function StatCard({
  label,
  value,
  unit,
  precision = 0,
  trend,
  description,
  duration = 1.2,
  className,
}: StatCardProps) {
  const prefersReducedMotion = useReducedMotion();
  const { ref, display, isInView } = useCountUp<HTMLDivElement>(value, duration);

  const formatNumber = (input: number) =>
    input.toLocaleString(undefined, {
      minimumFractionDigits: precision,
      maximumFractionDigits: precision,
    });

  const srSummary = [
    `${label}: ${formatNumber(value)}${unit ? ` ${unit}` : ""}`,
    trend ? `trending ${trend.direction} ${trend.value}` : null,
    description,
  ]
    .filter(Boolean)
    .join(". ");

  const TrendIcon = trend?.direction === "down" ? TrendingDown : TrendingUp;
  const trendSentiment = trend
    ? (trend.sentiment ?? (trend.direction === "up" ? "positive" : "negative"))
    : null;

  return (
    <MotionSurface
      ref={ref}
      elevated
      initial={prefersReducedMotion ? false : { opacity: 0, y: 16 }}
      animate={isInView || prefersReducedMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 16 }}
      transition={{ duration: 0.5, ease: EASE_STANDARD }}
      className={cn("flex flex-col gap-2 p-6", className)}
    >
      <span className="sr-only">{srSummary}</span>
      <div aria-hidden="true" className="flex flex-col gap-2">
        <span className="font-mono text-caption uppercase tracking-wide text-text-muted">
          {label}
        </span>
        <div className="flex items-baseline gap-1">
          <span className="font-mono text-heading-xl tabular-nums text-text-primary">
            {formatNumber(display)}
          </span>
          {unit ? <span className="text-label-md text-text-muted">{unit}</span> : null}
        </div>
        {trend ? (
          <span
            className={cn(
              "inline-flex w-fit items-center gap-1 font-mono text-label-md",
              trendSentiment === "positive" ? "text-success" : "text-danger",
            )}
          >
            <TrendIcon className="size-3.5" aria-hidden="true" />
            {trend.value}
          </span>
        ) : null}
        {description ? <p className="text-body-sm text-text-secondary">{description}</p> : null}
      </div>
    </MotionSurface>
  );
}
