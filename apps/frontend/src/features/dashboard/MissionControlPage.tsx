import type { ConstructorStandingEntry, DriverStandingEntry } from "@pit-wall-insight/shared-types";
import { Hero, Section, Stat, StatGroup } from "@pit-wall-insight/ui";
import type { ReactNode } from "react";

import { EmptyState } from "../../lib/empty-state.js";
import { QueryError } from "../../lib/query-error.js";
import { useDashboard, useDashboardHighlights } from "./queries.js";

/**
 * Mission Control — the flagship page (docs/assets/04_LAYOUT_SYSTEM.md —
 * "Dashboard Layout": Current Season -> Standings -> Key Metrics -> Recent
 * Events; "never place secondary information above primary insights").
 *
 * Rebuilt around the four-slot editorial model instead of a widget grid:
 * one dot-matrix hero statement (the only page in the app that uses the
 * "statement" title treatment — reserved for this one moment), one
 * dominant analytical focus (the championship gap — "how close is the
 * title fight," not just a restated points total), then standings and
 * performance figures clearly demoted below it. The static "Features"/
 * "Statistics" marketing bands are gone — the sidebar already covers
 * navigation, and restating capability areas in prose duplicated it.
 *
 * `Section`/`Stat`/`StatGroup` replace `Widget`/`WidgetGrid`/`Dashboard` —
 * no bordered boxes anywhere on this page.
 */
export function MissionControlPage() {
  const dashboardQuery = useDashboard();
  const highlightsQuery = useDashboardHighlights();
  const dashboard = dashboardQuery.data;
  const highlights = highlightsQuery.data;

  return (
    <>
      <Hero
        titleVariant="statement"
        eyebrow="Mission Control"
        title="Every lap. Every decision. Understood."
        description="Formula One telemetry, strategy, and race intelligence in one engineering-grade analytics platform."
        actions={[
          { label: "Explore season", href: "/season", variant: "primary" },
          { label: "View telemetry", href: "/telemetry", variant: "secondary" },
        ]}
      />

      <Section
        eyebrow="Live data"
        title="Season at a glance"
        description="The championship fight, right now."
      >
        {dashboardQuery.isError ? (
          <QueryError />
        ) : dashboardQuery.isPending ? (
          <EmptyState message="Syncing telemetry…" />
        ) : (
          <StatGroup>
            <Stat
              label="Championship gap"
              value={dashboard?.championshipGap ?? "—"}
              variant="hero"
              caption="Between P1 and P2"
              {...(dashboard?.championshipGap != null && { unit: "pts" })}
            />
            <Stat label="Season" value={dashboard?.season ?? "—"} />
            <Stat label="Leader" value={dashboard?.championDriver ?? "—"} />
            <Stat label="Leading team" value={dashboard?.championConstructor ?? "—"} />
          </StatGroup>
        )}
      </Section>

      <Section title="Standings" description="Top five in each championship.">
        <div className="grid grid-cols-1 gap-x-16 gap-y-10 laptop:grid-cols-2">
          <StandingsColumn
            title="Drivers"
            href="/drivers"
            linkLabel="Driver Dossier"
            loading={dashboardQuery.isPending}
            error={dashboardQuery.isError}
          >
            <DriverStandingsList entries={dashboard?.driverStandings ?? []} />
          </StandingsColumn>
          <StandingsColumn
            title="Constructors"
            href="/constructors"
            linkLabel="Constructor Intelligence"
            loading={dashboardQuery.isPending}
            error={dashboardQuery.isError}
          >
            <ConstructorStandingsList entries={dashboard?.constructorStandings ?? []} />
          </StandingsColumn>
        </div>
      </Section>

      <Section
        title="Performance"
        description="Fastest lap, quickest average pit stop, and overtakes recorded this season."
      >
        {dashboardQuery.isError ? (
          <QueryError />
        ) : dashboardQuery.isPending ? (
          <EmptyState message="Syncing telemetry…" />
        ) : (
          <StatGroup>
            <Stat
              label="Fastest lap"
              value={dashboard?.fastestLapTime != null ? dashboard.fastestLapTime.toFixed(3) : "—"}
              unit="s"
              {...(dashboard?.fastestLapDriver != null && { caption: dashboard.fastestLapDriver })}
            />
            <Stat
              label="Avg. pit stop"
              value={dashboard?.fastestPitstop != null ? dashboard.fastestPitstop.toFixed(1) : "—"}
              unit="s"
            />
            <Stat
              label="Overtakes"
              value={
                dashboard?.averageOvertakes != null ? dashboard.averageOvertakes.toFixed(1) : "—"
              }
            />
          </StatGroup>
        )}
      </Section>

      <Section
        title="Latest race"
        description={highlights?.raceName ?? "Most recent completed round."}
      >
        {highlightsQuery.isError ? (
          <QueryError />
        ) : highlightsQuery.isPending ? (
          <EmptyState message="Syncing telemetry…" />
        ) : (
          <StatGroup>
            <Stat label="Winner" value={highlights?.winner ?? "—"} />
            <Stat label="Pole" value={highlights?.pole ?? "—"} />
            <Stat label="Fastest lap" value={highlights?.fastestLap ?? "—"} />
            <Stat label="Retirements" value={highlights?.retirements ?? "—"} />
          </StatGroup>
        )}
      </Section>
    </>
  );
}

function StandingsColumn({
  title,
  href,
  linkLabel,
  loading,
  error,
  children,
}: {
  title: string;
  href: string;
  linkLabel: string;
  loading: boolean;
  error: boolean;
  children: ReactNode;
}) {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-baseline justify-between gap-4">
        <h3 className="font-display text-heading-sm text-text-primary">{title}</h3>
        <a
          href={href}
          className="shrink-0 text-label-md text-constructor-primary transition-colors duration-(--duration-fast) ease-standard hover:text-accent-hover"
        >
          {linkLabel}
        </a>
      </div>
      {error ? <QueryError /> : loading ? <EmptyState message="Syncing telemetry…" /> : children}
    </div>
  );
}

/** Shared row markup for both standings lists below — same visual
 * convention already used by the Season Explorer's race calendar
 * (`features/season/SeasonExplorerPage.tsx`). */
function StandingsRow({
  position,
  label,
  points,
}: {
  position: number;
  label: string;
  points: number;
}) {
  return (
    <li className="flex items-center justify-between gap-3 border-b border-border-subtle pb-2 last:border-b-0 last:pb-0">
      <span className="flex items-center gap-3">
        <span className="font-mono text-caption uppercase tracking-wide text-text-muted">
          {position}
        </span>
        <span className="text-body-sm text-text-primary">{label}</span>
      </span>
      <span className="font-mono text-caption tabular-nums text-text-muted">{points} pts</span>
    </li>
  );
}

function DriverStandingsList({ entries }: { entries: readonly DriverStandingEntry[] }) {
  if (entries.length === 0) {
    return <EmptyState message="No standings yet" />;
  }
  return (
    <ol className="flex flex-col gap-2">
      {entries.slice(0, 5).map((entry) => (
        <StandingsRow
          key={entry.position}
          position={entry.position}
          label={entry.driver}
          points={entry.points}
        />
      ))}
    </ol>
  );
}

function ConstructorStandingsList({ entries }: { entries: readonly ConstructorStandingEntry[] }) {
  if (entries.length === 0) {
    return <EmptyState message="No standings yet" />;
  }
  return (
    <ol className="flex flex-col gap-2">
      {entries.slice(0, 5).map((entry) => (
        <StandingsRow
          key={entry.position}
          position={entry.position}
          label={entry.constructor}
          points={entry.points}
        />
      ))}
    </ol>
  );
}
