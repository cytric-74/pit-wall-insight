import { motion, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";

import { cn } from "../lib/cn.js";
import { sectionReveal } from "../lib/motion.js";
import { Container } from "./Container.js";

export interface SectionProps {
  /** Small uppercase mono label above the title, e.g. "Season Performance". */
  eyebrow?: string;
  title: string;
  description?: string;
  /** The one dominant analytical focus for this section — rendered large, unboxed. */
  children?: ReactNode;
  className?: string;
  /** Caps content to the readable measure instead of the full content width — for text-heavy sections. */
  narrow?: boolean;
}

/**
 * Replaces `Widget`/`WidgetGrid` as the default page-composition primitive
 * (docs/assets/04_LAYOUT_SYSTEM.md — "Section Structure": Title -> Supporting
 * Context -> Primary Visualization -> Supporting Details -> Actions;
 * "Card Philosophy: cards exist only when grouping improves understanding,
 * never to fill space").
 *
 * Deliberately has no background, border, or radius — a page is composed
 * of Sections separated by whitespace and rhythm, not boxes. Containers
 * (`Surface`/`Card`) remain reserved for dialogs, dropdowns, popovers, and
 * the command palette, per the redesign brief.
 *
 * Reveals once on scroll into view (fade -> translate -> settle, matching
 * every other entrance in the system) rather than on every re-render.
 */
export function Section({
  eyebrow,
  title,
  description,
  children,
  className,
  narrow = false,
}: SectionProps) {
  const prefersReducedMotion = useReducedMotion();

  return (
    <motion.section
      initial={prefersReducedMotion ? false : "hidden"}
      whileInView="show"
      viewport={{ once: true, margin: "-80px" }}
      variants={sectionReveal}
      className={cn("flex flex-col gap-8", className)}
    >
      <Container className={cn(narrow && "max-w-(--reading-width)")}>
        <div className="flex max-w-2xl flex-col gap-3">
          {eyebrow ? (
            <span className="font-mono text-caption uppercase tracking-telemetry text-text-muted">
              {eyebrow}
            </span>
          ) : null}
          <h2 className="font-display text-heading-xl text-text-primary">{title}</h2>
          {description ? <p className="text-body-lg text-text-secondary">{description}</p> : null}
        </div>
      </Container>
      {children ? <Container>{children}</Container> : null}
    </motion.section>
  );
}
