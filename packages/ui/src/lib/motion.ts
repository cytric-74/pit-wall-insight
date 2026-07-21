import { animate, useInView, useReducedMotion, type Variants } from "framer-motion";
import { useEffect, useRef, useState } from "react";

/**
 * Shared Framer Motion primitives (docs/assets/05_MOTION_SYSTEM.md).
 * Extracted once Hero and Features both needed the identical
 * stagger-reveal pattern — keeps every section's motion visually
 * consistent rather than each one inventing its own timing.
 */

/** Matches --ease-standard (easeOutExpo) — packages/config/tailwind/tokens.css. */
export const EASE_STANDARD = [0.16, 1, 0.3, 1] as const;
/** Matches --ease-out (easeOutQuart) — used for entrances specifically. */
export const EASE_ENTER = [0.25, 1, 0.5, 1] as const;

/** Reveals children in sequence, never simultaneously ("Hero Motion" / "Card Motion"). */
export const staggerContainer: Variants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.12, delayChildren: 0.05 } },
};

export const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: EASE_STANDARD } },
};

/**
 * Section-level entrance ("Entry Motion": fade -> translate -> settle,
 * never scale-from-zero/rotate/bounce). Slightly larger travel distance
 * than `fadeInUp` since it's meant for whole sections, not list items.
 */
export const sectionReveal: Variants = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: EASE_STANDARD } },
};

/**
 * SVG stroke draw-in ("Telemetry Motion: lines draw progressively, never
 * appear instantly") — for track blueprints, circuit graphics, and any
 * other line-art that should feel like it's being plotted live rather than
 * simply fading in. Apply to a `motion.path`'s `variants` with an
 * `initial`/`animate` of "hidden"/"show".
 */
export const drawPath: Variants = {
  hidden: { pathLength: 0, opacity: 0 },
  show: { pathLength: 1, opacity: 1, transition: { duration: 1.6, ease: EASE_STANDARD } },
};

/**
 * Numeric count-up ("Numbers: every important metric animates... uses
 * easing, never linear"). Starts once the element scrolls into view
 * (`once: true` — never re-triggers on repeated scroll), and returns the
 * final value immediately under reduced motion rather than animating.
 *
 * Extracted from `StatCard` so the same behavior is available to any
 * freestanding number (`Stat`, KPI readouts, hero stats) without every
 * consumer re-implementing the `useInView` + `animate` wiring.
 */
export function useCountUp<T extends HTMLElement = HTMLElement>(value: number, duration = 1.2) {
  const ref = useRef<T>(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });
  const prefersReducedMotion = useReducedMotion();
  const [display, setDisplay] = useState(() => (prefersReducedMotion ? value : 0));

  useEffect(() => {
    if (!isInView) return;
    if (prefersReducedMotion) {
      setDisplay(value);
      return;
    }
    const controls = animate(0, value, {
      duration,
      ease: EASE_STANDARD,
      onUpdate: setDisplay,
    });
    return () => controls.stop();
  }, [isInView, value, duration, prefersReducedMotion]);

  return { ref, display, isInView };
}
