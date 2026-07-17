import { motion, useReducedMotion } from "framer-motion";

import { StatCard, type StatCardProps } from "../cards/StatCard.js";
import { cn } from "../lib/cn.js";
import { fadeInUp as itemVariants, staggerContainer as containerVariants } from "../lib/motion.js";
import { Container } from "./Container.js";

export type StatisticsItem = Omit<StatCardProps, "className">;

export interface StatisticsProps {
  eyebrow?: string;
  title: string;
  description?: string;
  stats: readonly StatisticsItem[];
  className?: string;
}

/**
 * A row of KPI panels (docs/09_COMPONENT_LIBRARY.md — "KPI Components").
 * Only the heading block uses the shared stagger-reveal — each StatCard
 * already drives its own fade-in and count-up off a single `useInView`
 * observer, so wrapping the grid in a second one would just double up on
 * the same visibility check.
 */
export function Statistics({ eyebrow, title, description, stats, className }: StatisticsProps) {
  const prefersReducedMotion = useReducedMotion();
  const initial = prefersReducedMotion ? "show" : "hidden";

  return (
    <section className={cn("py-(--section-gap)", className)}>
      <Container className="flex flex-col gap-12">
        <motion.div
          initial={initial}
          whileInView="show"
          viewport={{ once: true, margin: "-80px" }}
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

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 laptop:grid-cols-4">
          {stats.map((stat) => (
            <StatCard key={stat.label} {...stat} />
          ))}
        </div>
      </Container>
    </section>
  );
}
