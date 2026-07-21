import { motion, useReducedMotion } from "framer-motion";
import { Children } from "react";
import type { ReactNode } from "react";

import { cn } from "../lib/cn.js";
import { EASE_STANDARD, useCountUp } from "../lib/motion.js";
import { Divider } from "../ui/Divider.js";

export interface StatProps {
  label: string;
  /** Numeric values count up on scroll into view; strings render as-is (e.g. "—", a name, a time). */
  value: number | string;
  unit?: string;
  /** Decimal places when `value` is numeric. Defaults to 0. */
  precision?: number;
  duration?: number;
  /**
   * "default" is the everyday freestanding KPI (mono, tabular). "hero" is
   * the dot-matrix "giant numerical moment" — reserve for the single most
   * important number on a page; never use it twice on the same screen
   * (docs/assets/01_VISUAL_LANGUAGE.md — "never introduce competing focal
   * points").
   */
  variant?: "default" | "hero";
  /** Small supporting line below the value — "Delta -> Supporting Context" (e.g. a driver name behind a lap time). */
  caption?: string;
  className?: string;
}

/**
 * A freestanding number — no box, no border, no background. Replaces the
 * boxed `StatCard` as the default KPI treatment (see the redesign brief:
 * "STOP designing with cards... allow driver numbers to become background
 * graphics... everything should feel editorial rather than boxed").
 *
 * Structure follows the documented KPI Panel rhythm (Label -> Value ->
 * Unit) minus the panel itself. Numeric values animate with `useCountUp`;
 * string values (a name, a "—" empty state, a formatted time) render
 * immediately since there's nothing to count toward.
 */
export function Stat({
  label,
  value,
  unit,
  precision = 0,
  duration = 1.2,
  variant = "default",
  caption,
  className,
}: StatProps) {
  const prefersReducedMotion = useReducedMotion();
  const isNumeric = typeof value === "number";
  const { ref, display, isInView } = useCountUp<HTMLDivElement>(isNumeric ? value : 0, duration);

  const formatted = isNumeric
    ? display.toLocaleString(undefined, {
        minimumFractionDigits: precision,
        maximumFractionDigits: precision,
      })
    : value;

  return (
    <motion.div
      ref={isNumeric ? ref : undefined}
      initial={prefersReducedMotion ? false : { opacity: 0, y: 12 }}
      animate={isInView || !isNumeric || prefersReducedMotion ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5, ease: EASE_STANDARD }}
      className={cn("flex flex-col gap-1.5", className)}
    >
      <span className="font-mono text-caption uppercase tracking-wide text-text-muted">
        {label}
      </span>
      <div className="flex items-baseline gap-1.5">
        <span
          className={cn(
            "tabular-nums text-text-primary",
            variant === "hero"
              ? "font-dotmatrix text-display-md tracking-tight"
              : "font-mono text-heading-xl",
          )}
        >
          {formatted}
        </span>
        {unit ? <span className="text-label-md text-text-muted">{unit}</span> : null}
      </div>
      {caption ? (
        <span className="font-mono text-label-sm uppercase tracking-wide text-text-muted">
          {caption}
        </span>
      ) : null}
    </motion.div>
  );
}

export interface StatGroupProps {
  children: ReactNode;
  className?: string;
}

/**
 * Lays out a row of `Stat`s separated by a thin vertical divider between
 * neighbors — never a border around each one. This is the freestanding
 * replacement for a row of boxed KPI tiles.
 */
export function StatGroup({ children, className }: StatGroupProps) {
  const items = Children.toArray(children);
  return (
    <div className={cn("flex flex-wrap items-start gap-x-8 gap-y-6", className)}>
      {items.map((item, index) => (
        <div key={index} className="flex items-start gap-8">
          {item}
          {index < items.length - 1 ? (
            <Divider orientation="vertical" className="hidden h-12 sm:block" />
          ) : null}
        </div>
      ))}
    </div>
  );
}
