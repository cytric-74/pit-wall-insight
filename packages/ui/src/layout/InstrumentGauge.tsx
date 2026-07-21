import { motion, useReducedMotion, useInView } from "framer-motion";
import { useRef } from "react";

import { cn } from "../lib/cn.js";
import { EASE_STANDARD } from "../lib/motion.js";

export interface InstrumentGaugeProps {
  label: string;
  /** 0-100. Values outside this range are clamped. */
  value: number;
  /** Defaults to "LOW" / "HIGH" — override for domain-specific anchors (e.g. "SOFT" / "HARD"). */
  minLabel?: string;
  maxLabel?: string;
  /** Formatted readout shown next to the label, e.g. "2.4s" or "18%". Optional. */
  valueLabel?: string;
  className?: string;
}

/**
 * A single-dimension technical readout — a linear meter with HIGH/LOW (or
 * domain-specific) anchors, replacing plain line charts / `<dl>` rows for
 * metrics that are really just "where does this sit between two ends"
 * (pit-stop efficiency, reliability, tyre wear). Matches
 * docs/assets/09_COMPONENT_STYLING.md — "Progress Bars: Thin. Accurate.
 * Constructor accent. Never gradients."
 *
 * The fill animates in on scroll into view rather than snapping to width
 * immediately, consistent with every other data-reveal in the system.
 */
export function InstrumentGauge({
  label,
  value,
  minLabel = "LOW",
  maxLabel = "HIGH",
  valueLabel,
  className,
}: InstrumentGaugeProps) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });
  const prefersReducedMotion = useReducedMotion();
  const clamped = Math.max(0, Math.min(100, value));

  return (
    <div ref={ref} className={cn("flex flex-col gap-2", className)}>
      <div className="flex items-baseline justify-between">
        <span className="font-mono text-caption uppercase tracking-wide text-text-muted">
          {label}
        </span>
        {valueLabel ? (
          <span className="font-mono text-label-md tabular-nums text-text-primary">
            {valueLabel}
          </span>
        ) : null}
      </div>
      <div className="h-1 w-full overflow-hidden rounded-full bg-border-subtle">
        <motion.div
          className="h-full rounded-full bg-constructor-primary"
          initial={{ width: prefersReducedMotion ? `${clamped}%` : 0 }}
          animate={{ width: isInView || prefersReducedMotion ? `${clamped}%` : 0 }}
          transition={{ duration: 0.8, ease: EASE_STANDARD }}
        />
      </div>
      <div className="flex items-center justify-between font-mono text-label-sm uppercase tracking-wide text-text-disabled">
        <span>{minLabel}</span>
        <span>{maxLabel}</span>
      </div>
    </div>
  );
}
