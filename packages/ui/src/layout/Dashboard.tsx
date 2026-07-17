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
 * The dashboard shell (docs/assets/04_LAYOUT_SYSTEM.md — "Dashboard
 * Layout": Current Season -> Standings -> Key Metrics -> Recent Events ->
 * Navigation; "never place secondary information above primary
 * insights"). Provides the heading and Container; the grid itself is left
 * to `WidgetGrid` since a season-overview panel and a KPI tile are not the
 * same size.
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
 * Responsive 12-column widget grid. Items size themselves with
 * `laptop:col-span-*` (and optionally `sm:col-span-*` for the tablet
 * step) rather than the grid dictating a fixed layout for every widget.
 */
export function WidgetGrid({ children, className }: WidgetGridProps) {
  return (
    <div className={cn("grid grid-cols-1 gap-6 sm:grid-cols-2 laptop:grid-cols-12", className)}>
      {children}
    </div>
  );
}
