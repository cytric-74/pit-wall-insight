import { motion, useReducedMotion } from "framer-motion";
import type { LucideIcon } from "lucide-react";

import { cn } from "../lib/cn.js";
import { fadeInUp as itemVariants, staggerContainer as containerVariants } from "../lib/motion.js";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/Card.js";
import { Container } from "./Container.js";

export interface Feature {
  title: string;
  description: string;
  icon: LucideIcon;
  href?: string;
}

export interface FeaturesProps {
  eyebrow?: string;
  title: string;
  description?: string;
  features: readonly Feature[];
  className?: string;
}

/**
 * A "Section" + "Grid" of "Cards" (docs/09_COMPONENT_LIBRARY.md — Layout
 * Components / Cards), used to summarize the platform's analytical
 * capability areas. Unlike the Hero (visible immediately on load), this
 * section typically sits below the fold, so it reveals on scroll
 * (`whileInView`, `once: true` — never re-triggers, per
 * docs/assets/05_MOTION_SYSTEM.md: "motion should never distract").
 */
export function Features({ eyebrow, title, description, features, className }: FeaturesProps) {
  const prefersReducedMotion = useReducedMotion();
  const initial = prefersReducedMotion ? "show" : "hidden";
  const viewport = { once: true, margin: "-80px" } as const;

  return (
    <section className={cn("py-(--section-gap)", className)}>
      <Container className="flex flex-col gap-12">
        <motion.div
          initial={initial}
          whileInView="show"
          viewport={viewport}
          variants={containerVariants}
          className="flex max-w-2xl flex-col gap-4"
        >
          {eyebrow ? (
            <motion.span
              variants={itemVariants}
              className="font-mono text-caption uppercase tracking-telemetry text-text-muted"
            >
              {eyebrow}
            </motion.span>
          ) : null}
          <motion.h2
            variants={itemVariants}
            className="font-display text-heading-xl text-text-primary"
          >
            {title}
          </motion.h2>
          {description ? (
            <motion.p variants={itemVariants} className="text-body-lg text-text-secondary">
              {description}
            </motion.p>
          ) : null}
        </motion.div>

        <motion.div
          initial={initial}
          whileInView="show"
          viewport={viewport}
          variants={containerVariants}
          className="grid grid-cols-1 gap-6 sm:grid-cols-2 laptop:grid-cols-3"
        >
          {features.map((feature) => (
            <motion.div key={feature.title} variants={itemVariants} className="h-full">
              <FeatureCard feature={feature} />
            </motion.div>
          ))}
        </motion.div>
      </Container>
    </section>
  );
}

function FeatureCard({ feature }: { feature: Feature }) {
  const Icon = feature.icon;

  const card = (
    <Card className="group h-full transition duration-(--duration-card) ease-standard hover:-translate-y-1 hover:border-constructor-primary/40 hover:bg-surface-hover hover:shadow-panel">
      <CardHeader className="gap-3">
        <span className="flex size-10 items-center justify-center rounded-md border border-border-default bg-surface-elevated text-constructor-primary transition-colors duration-(--duration-fast) ease-standard group-hover:border-constructor-primary/40">
          <Icon className="size-5" aria-hidden="true" />
        </span>
        <CardTitle className="text-heading-sm">{feature.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <CardDescription>{feature.description}</CardDescription>
      </CardContent>
    </Card>
  );

  if (feature.href) {
    return (
      <a href={feature.href} className="block h-full no-underline">
        {card}
      </a>
    );
  }

  return card;
}
