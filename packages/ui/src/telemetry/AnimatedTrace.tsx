import { motion, useReducedMotion } from "framer-motion";

import { drawPath } from "../lib/motion.js";

export interface AnimatedTraceProps {
  /** SVG path `d` attribute — the line to draw. */
  d: string;
  viewBox: string;
  className?: string;
  ariaLabel: string;
  strokeWidth?: number;
  /** Optional faint frame rect drawn behind the trace (blueprint-style border). */
  frame?: boolean;
}

/**
 * A single SVG stroke that draws itself in on mount ("Telemetry Motion:
 * lines draw progressively, never appear instantly") instead of simply
 * appearing — for track blueprints, circuit graphics, and any other
 * line-art that should read as being plotted live. Reduced motion renders
 * the finished path immediately.
 *
 * Kept inside the design system (rather than each page importing
 * framer-motion directly) so animation stays centralized here, consistent
 * with every other motion primitive in the app.
 */
export function AnimatedTrace({
  d,
  viewBox,
  className,
  ariaLabel,
  strokeWidth = 2.5,
  frame = true,
}: AnimatedTraceProps) {
  const prefersReducedMotion = useReducedMotion();

  return (
    <svg viewBox={viewBox} className={className} fill="none" role="img" aria-label={ariaLabel}>
      {frame ? (
        <rect
          x="0.5"
          y="0.5"
          width={Number(viewBox.split(" ")[2]) - 1}
          height={Number(viewBox.split(" ")[3]) - 1}
          rx="16"
          className="stroke-border-subtle"
          opacity={0.4}
        />
      ) : null}
      {prefersReducedMotion ? (
        <path d={d} stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" />
      ) : (
        <motion.path
          key={d}
          d={d}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          initial="hidden"
          animate="show"
          variants={drawPath}
        />
      )}
    </svg>
  );
}
