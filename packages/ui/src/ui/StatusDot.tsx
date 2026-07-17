import { motion, useReducedMotion } from "framer-motion";

import { cn } from "../lib/cn.js";

export interface StatusDotProps {
  className?: string;
}

/**
 * Small pulsing status-LED dot — the "Nothing Design" accent-dot reference
 * named alongside Apple/Bloomberg Terminal in docs/assets/00_BRANDING.md.
 * Used anywhere an eyebrow/label wants that telemetry-status accent
 * (Hero, Footer, ...) so the motif stays visually identical everywhere.
 */
export function StatusDot({ className }: StatusDotProps) {
  const prefersReducedMotion = useReducedMotion();

  return (
    <span className={cn("relative flex size-2", className)}>
      {!prefersReducedMotion ? (
        <motion.span
          className="absolute inline-flex size-full rounded-full bg-constructor-primary"
          animate={{ opacity: [0.6, 0, 0.6], scale: [1, 1.8, 1] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        />
      ) : null}
      <span className="relative inline-flex size-2 rounded-full bg-constructor-primary" />
    </span>
  );
}
