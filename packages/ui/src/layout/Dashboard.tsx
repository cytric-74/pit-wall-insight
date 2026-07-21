import type { ReactNode } from "react";

import { cn } from "../lib/cn.js";
import { Container } from "./Container.js";

export interface DashboardProps {
  eyebrow?: string;
  title: string;
  description?: string;
  /** The widget grid (see `WidgetGrid`) — composed by the caller since widget sizes vary. */
  children: ReactNode;
  className?: string;
}

/**
 * @deprecated Superseded by `Section` as part of the editorial redesign —
 * "Section Structure" replaces "Dashboard Layout" as the page-composition
 * primitive (see the redesign strategy: "STOP designing with cards...
 * everything should feel editorial rather than boxed"). Kept only until
 * every page still importing `Dashboard`/`WidgetGrid` has migrated to
 * `Section`; do not use in new code.
 */
export function Dashboard({ eyebrow, title, description, children, className }: DashboardProps) {
  return (
    <section className={cn("py-(--section-gap)", className)}>
      <Container className="flex flex-col gap-8">
        <div className="flex max-w-2xl flex-col gap-4">
          {eyebrow ? (
            <span className="font-mono text-caption uppercase tracking-telemetry text-text-muted">
              {eyebrow}
            </span>
          ) : null}
          <h2 className="font-display text-heading-xl text-text-primary">{title}</h2>
          {description ? <p className="text-body-lg text-text-secondary">{description}</p> : null}
        </div>
        {children}
      </Container>
    </section>
  );
}

export interface WidgetGridProps {
  children: ReactNode;
  className?: string;
}

/**
 * @deprecated A grid of equal-weight boxes is exactly what the editorial
 * redesign removes ("never let every widget compete equally" — every page
 * needs one dominant focal point, not N same-size cells). Compose pages
 * from `Section` + `Stat`/`StatGroup`/`InstrumentGauge` + charts directly
 * instead, with hierarchy expressed through type scale and layout, not
 * `col-span` math.
 */
export function WidgetGrid({ children, className }: WidgetGridProps) {
  return (
    <div className={cn("grid grid-cols-1 gap-6 sm:grid-cols-2 laptop:grid-cols-12", className)}>
      {children}
    </div>
  );
}
