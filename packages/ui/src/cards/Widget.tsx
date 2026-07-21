import type { ReactNode } from "react";

import { cn } from "../lib/cn.js";
import { Skeleton } from "../loading/Skeleton.js";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/Card.js";

export interface WidgetProps {
  title: string;
  description?: string;
  /** "View all"-style link to the full page this widget summarizes. */
  href?: string;
  linkLabel?: string;
  /** Shows skeleton rows instead of `children` — for content not wired to real data yet. */
  loading?: boolean;
  className?: string;
  children?: ReactNode;
}

/**
 * @deprecated Boxed dashboard panels are the thing the editorial redesign
 * removes — see the redesign strategy: "Only use containers where
 * functionally necessary: dialogs, dropdowns, popovers, command palette."
 * Use `Section` for page composition and `Stat`/`InstrumentGauge` for the
 * content that used to live inside a `Widget`. Kept only until every page
 * has migrated (tracked page by page: Mission Control, Driver Dossier,
 * Circuit Explorer, Constructor Intelligence, Race Playback, Telemetry,
 * Strategy, Season, Settings) — delete once none remain.
 */
export function Widget({
  title,
  description,
  href,
  linkLabel = "View all",
  loading = false,
  className,
  children,
}: WidgetProps) {
  return (
    <Card className={cn("flex h-full flex-col gap-4", className)}>
      <CardHeader className="flex-row items-start justify-between gap-4">
        <div className="flex flex-col gap-1">
          <CardTitle className="text-heading-sm">{title}</CardTitle>
          {description ? <CardDescription>{description}</CardDescription> : null}
        </div>
        {href ? (
          <a
            href={href}
            className="shrink-0 text-label-md text-constructor-primary transition-colors duration-(--duration-fast) ease-standard hover:text-accent-hover"
          >
            {linkLabel}
          </a>
        ) : null}
      </CardHeader>
      <CardContent className="flex-1" aria-busy={loading}>
        {loading ? (
          <>
            <span
              role="status"
              aria-live="polite"
              className="sr-only"
            >{`Loading ${title} data…`}</span>
            <div aria-hidden="true" className="flex flex-col gap-3">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
              <Skeleton className="h-4 w-2/3" />
            </div>
          </>
        ) : (
          children
        )}
      </CardContent>
    </Card>
  );
}
