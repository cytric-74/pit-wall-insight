import { motion, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";

import { cn } from "../lib/cn.js";
import {
  EASE_STANDARD,
  fadeInUp as itemVariants,
  staggerContainer as containerVariants,
} from "../lib/motion.js";
import { Button } from "../ui/Button.js";
import { StatusDot } from "../ui/StatusDot.js";
import { Container } from "./Container.js";

export interface HeroStat {
  label: string;
  value: string;
  unit?: string;
}

export interface HeroAction {
  label: string;
  href?: string;
  onClick?: () => void;
  variant?: "primary" | "secondary" | "ghost";
}

export interface HeroProps {
  /** Small uppercase label above the title, e.g. "Mission Control". */
  eyebrow?: string;
  title: string;
  description?: string;
  stats?: readonly HeroStat[];
  actions?: readonly HeroAction[];
  className?: string;
}

/**
 * The Hero section every page begins with (docs/assets/04_LAYOUT_SYSTEM.md
 * — "Hero Section": Page Title, Description, Session Context, Filters,
 * Quick Actions; docs/09_COMPONENT_LIBRARY.md — "Hero Components").
 *
 * Reveal follows docs/assets/05_MOTION_SYSTEM.md's "Hero Motion": Background
 * -> Title -> Subtitle -> Metadata -> Actions -> Illustration -> Ambient —
 * nothing appears simultaneously. `useReducedMotion` collapses every
 * transition to an immediate, final-state render
 * (docs/assets/13_ACCESSIBILITY_VISUALS.md — "Reduced Motion").
 *
 * Typography leans on the "Nothing Design" reference named alongside
 * Apple/Bloomberg Terminal in docs/assets/00_BRANDING.md: a pulsing accent
 * dot as a status-LED glyph, dot-matrix (Silkscreen) numerals for the stat
 * row, and wide-tracked monospace labels — the same dot-matrix vocabulary
 * already reserved for telemetry/live-timing elsewhere in the system.
 */
export function Hero({ eyebrow, title, description, stats, actions, className }: HeroProps) {
  const prefersReducedMotion = useReducedMotion();
  const initial = prefersReducedMotion ? "show" : "hidden";

  return (
    <section className={cn("relative overflow-hidden", className)}>
      <HeroAtmosphere reduced={Boolean(prefersReducedMotion)} />

      <Container className="relative py-(--hero-spacing)">
        <div className="grid items-center gap-12 laptop:grid-cols-[minmax(0,1fr)_320px]">
          <motion.div
            initial={initial}
            animate="show"
            variants={containerVariants}
            className="flex flex-col gap-6"
          >
            {eyebrow ? (
              <motion.div variants={itemVariants} className="flex items-center gap-2">
                <StatusDot />
                <span className="font-mono text-caption uppercase tracking-telemetry text-text-muted">
                  {eyebrow}
                </span>
              </motion.div>
            ) : null}

            <motion.h1
              variants={itemVariants}
              className="text-balance font-display text-display-md tracking-tight text-text-primary laptop:text-display-lg"
            >
              {title}
            </motion.h1>

            {description ? (
              <motion.p
                variants={itemVariants}
                className="max-w-2xl text-body-lg text-text-secondary"
              >
                {description}
              </motion.p>
            ) : null}

            {actions?.length ? (
              <motion.div variants={itemVariants} className="flex flex-wrap items-center gap-3">
                {actions.map((action) => (
                  <HeroActionButton key={action.label} action={action} />
                ))}
              </motion.div>
            ) : null}

            {stats?.length ? (
              <motion.dl
                variants={itemVariants}
                className="grid grid-cols-2 gap-6 border-t border-border-subtle pt-6 sm:grid-cols-4"
              >
                {stats.map((stat) => (
                  <div key={stat.label} className="flex flex-col gap-1">
                    <dt className="font-mono text-caption uppercase tracking-wide text-text-muted">
                      {stat.label}
                    </dt>
                    <dd className="font-dotmatrix text-heading-md tabular-nums text-text-primary">
                      {stat.value}
                      {stat.unit ? (
                        <span className="ml-1 font-body text-label-md text-text-muted">
                          {stat.unit}
                        </span>
                      ) : null}
                    </dd>
                  </div>
                ))}
              </motion.dl>
            ) : null}
          </motion.div>

          <motion.div
            initial={prefersReducedMotion ? { opacity: 1 } : { opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{
              duration: 0.6,
              delay: prefersReducedMotion ? 0 : 0.35,
              ease: EASE_STANDARD,
            }}
            className="hidden laptop:block"
            aria-hidden="true"
          >
            <HeroCircuitGraphic reduced={Boolean(prefersReducedMotion)} />
          </motion.div>
        </div>
      </Container>
    </section>
  );
}

function HeroActionButton({ action }: { action: HeroAction }) {
  const variant = action.variant ?? "primary";
  if (action.href) {
    return (
      <Button asChild variant={variant}>
        <a href={action.href}>{action.label}</a>
      </Button>
    );
  }
  return (
    <Button variant={variant} onClick={action.onClick}>
      {action.label}
    </Button>
  );
}

/**
 * Background atmosphere (docs/assets/16_VISUAL_EFFECTS.md — "Hero
 * Atmosphere": soft gradient, noise, telemetry overlay, ambient light —
 * effects remain behind content). Purely decorative, `aria-hidden`.
 */
function HeroAtmosphere({ reduced }: { reduced: boolean }) {
  return (
    <div aria-hidden="true" className="pointer-events-none absolute inset-0 -z-10">
      <div
        className="absolute -right-1/4 top-0 size-[42rem] rounded-full opacity-30 blur-3xl"
        style={{ backgroundColor: "var(--color-constructor-glow)" }}
      />
      <div
        className="absolute inset-0 opacity-[0.05]"
        style={{
          backgroundImage:
            "linear-gradient(to right, var(--color-border-subtle) 1px, transparent 1px), linear-gradient(to bottom, var(--color-border-subtle) 1px, transparent 1px)",
          backgroundSize: "48px 48px",
        }}
      />
      {!reduced ? (
        <motion.div
          className="absolute inset-x-0 h-px opacity-40"
          style={{
            backgroundImage:
              "linear-gradient(to right, transparent, var(--color-constructor-primary), transparent)",
          }}
          initial={{ top: "0%" }}
          animate={{ top: ["0%", "100%"] }}
          transition={{ duration: 6, repeat: Infinity, ease: "linear" }}
        />
      ) : null}
    </div>
  );
}

/**
 * Abstract circuit line-art — a placeholder for real circuit/car
 * photography (docs/assets/11_IMAGE_AND_MEDIA.md), drawn as a telemetry
 * trace: the stroke animates in with `pathLength`, matching "Telemetry
 * Motion: lines draw progressively, never appear instantly."
 */
function HeroCircuitGraphic({ reduced }: { reduced: boolean }): ReactNode {
  const path =
    "M20 90 L20 40 Q20 20 40 20 L120 20 Q140 20 140 40 L140 60 Q140 80 160 80 L220 80 Q240 80 240 100 L240 140 Q240 160 220 160 L60 160 Q20 160 20 130 Z";

  return (
    <svg
      viewBox="0 0 260 180"
      className="h-auto w-full text-constructor-primary"
      fill="none"
      role="img"
      aria-label="Abstract circuit trace"
    >
      <rect x="0.5" y="0.5" width="259" height="179" rx="16" className="stroke-border-default" />
      {reduced ? (
        <path d={path} stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      ) : (
        <motion.path
          d={path}
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 1 }}
          transition={{ duration: 1.8, delay: 0.4, ease: EASE_STANDARD }}
        />
      )}
    </svg>
  );
}
