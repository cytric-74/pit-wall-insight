import type { Variants } from "framer-motion";

/**
 * Shared Framer Motion primitives (docs/assets/05_MOTION_SYSTEM.md).
 * Extracted once Hero and Features both needed the identical
 * stagger-reveal pattern — keeps every section's motion visually
 * consistent rather than each one inventing its own timing.
 */

/** Matches --ease-standard (easeOutExpo) — packages/config/tailwind/tokens.css. */
export const EASE_STANDARD = [0.16, 1, 0.3, 1] as const;

/** Reveals children in sequence, never simultaneously ("Hero Motion" / "Card Motion"). */
export const staggerContainer: Variants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.12, delayChildren: 0.05 } },
};

export const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: EASE_STANDARD } },
};
