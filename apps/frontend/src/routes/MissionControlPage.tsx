import type { ConstructorStandingEntry, DriverStandingEntry } from "@pit-wall-insight/shared-types";
import { Dashboard, Features, Hero, Statistics, Widget, WidgetGrid } from "@pit-wall-insight/ui";

import { FEATURES } from "../constants/features.js";
import { STATISTICS } from "../constants/statistics.js";
import { useDashboard, useDashboardHighlights } from "../features/dashboard/queries.js";
import { EmptyState } from "../lib/empty-state.js";
import { QueryError } from "../lib/query-error.js";

/**
 * The Hero/Features/Statistics sections stay static marketing copy; the
 * `Dashboard` section is backed by `GET /dashboard` and
 * `GET /dashboard/highlights` (docs/08_API_SPECIFICATION.md — "Dashboard").
 */
export function MissionControlPage() {
  const dashboardQuery = useDashboard();
  const highlightsQuery = useDashboardHighlights();
  const dashboard = dashboardQuery.data;
  const highlights = highlightsQuery.data;

  return (
    <>
      <Hero
        eyebrow="Mission Control"
        title="Every lap. Every decision. Understood."
        description="Formula One telemetry, strategy, and race intelligence in one engineering-grade analytics platform."
        stats={[
          { label: "Seasons", value: "75" },
          { label: "Drivers", value: "20" },
          { label: "Constructors", value: "10" },
          { label: "Circuits", value: "24" },
        ]}
        actions={[
          { label: "Explore season", href: "/season", variant: "primary" },
          { label: "View telemetry", href: "/telemetry", variant: "secondary" },
        ]}
      />
      <Features
        eyebrow="Capabilities"
        title="One platform, every angle of the weekend."
        description="Each area is a dedicated analytics instrument, not another chart bolted onto a dashboard."
        features={FEATURES}
      />
      <Statistics
        eyebrow="This season"
        title="The numbers behind the season."
        description="A snapshot of what's been tracked so far."
        stats={STATISTICS}
      />
      <Dashboard
        eyebrow="Live data"
        title="Season at a glance."
        description="Current season, driver and constructor standings, and the latest race."
      >
        <WidgetGrid>
          <Widget
            title="Season overview"
            description="Current season progress"
            href="/season"
            linkLabel="Season Explorer"
            loading={dashboardQuery.isPending}
            className="sm:col-span-2 laptop:col-span-12"
          >
            {dashboardQuery.isError ? (
              <QueryError />
            ) : dashboard ? (
              <div className="flex flex-col gap-2">
                <span className="text-body-sm text-text-primary">{dashboard.season} season</span>
                <span className="text-caption text-text-muted">
                  Championship leader: {dashboard.championDriver ?? "—"}
                </span>
                <span className="text-caption text-text-muted">
                  Constructors leader: {dashboard.championConstructor ?? "—"}
                </span>
              </div>
            ) : null}
          </Widget>
          <Widget
            title="Driver standings"
            description="Championship order"
            href="/drivers"
            linkLabel="Driver Dossier"
            loading={dashboardQuery.isPending}
            className="laptop:col-span-6"
          >
            {dashboardQuery.isError ? (
              <QueryError />
            ) : dashboard ? (
              <DriverStandingsList entries={dashboard.driverStandings} />
            ) : null}
          </Widget>
          <Widget
            title="Constructor standings"
            description="Championship order"
            href="/constructors"
            linkLabel="Constructor Intelligence"
            loading={dashboardQuery.isPending}
            className="laptop:col-span-6"
          >
            {dashboardQuery.isError ? (
              <QueryError />
            ) : dashboard ? (
              <ConstructorStandingsList entries={dashboard.constructorStandings} />
            ) : null}
          </Widget>
          <KpiWidget
            title="Fastest lap"
            href="/telemetry"
            linkLabel="Telemetry Center"
            loading={dashboardQuery.isPending}
            isError={dashboardQuery.isError}
            value={
              dashboard?.fastestLapTime != null ? `${dashboard.fastestLapTime.toFixed(3)}s` : null
            }
            sublabel={dashboard?.fastestLapDriver ?? undefined}
          />
          <KpiWidget
            title="Avg. pit stop"
            href="/strategy"
            linkLabel="Strategy Lab"
            loading={dashboardQuery.isPending}
            isError={dashboardQuery.isError}
            value={
              dashboard?.fastestPitstop != null ? `${dashboard.fastestPitstop.toFixed(1)}s` : null
            }
          />
          <KpiWidget
            title="Overtakes"
            href="/races"
            linkLabel="Race Playback"
            loading={dashboardQuery.isPending}
            isError={dashboardQuery.isError}
            value={
              dashboard?.averageOvertakes != null ? dashboard.averageOvertakes.toFixed(1) : null
            }
          />
          <Widget
            title="Recent race summary"
            description="Latest completed round"
            href="/races"
            linkLabel="Race Playback"
            loading={highlightsQuery.isPending}
            className="sm:col-span-2 laptop:col-span-12"
          >
            {highlightsQuery.isError ? (
              <QueryError />
            ) : highlights ? (
              <div className="flex flex-col gap-2">
                <span className="text-body-sm text-text-primary">{highlights.raceName ?? "—"}</span>
                <span className="text-caption text-text-muted">
                  Winner: {highlights.winner ?? "—"}
                </span>
                <span className="text-caption text-text-muted">Pole: {highlights.pole ?? "—"}</span>
                <span className="text-caption text-text-muted">
                  Fastest lap: {highlights.fastestLap ?? "—"}
                </span>
              </div>
            ) : null}
          </Widget>
        </WidgetGrid>
      </Dashboard>
    </>
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
      <span className="text-caption text-text-muted">{points} pts</span>
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

interface KpiWidgetProps {
  title: string;
  href: string;
  linkLabel: string;
  loading: boolean;
  isError?: boolean | undefined;
  value?: string | null | undefined;
  sublabel?: string | undefined;
}

/**
 * A single-value KPI tile. Shows an explicit "no data" state rather than a
 * fabricated number whenever `value` is null/undefined — including once
 * wired up, since some metrics (e.g. average pit stop, pending Phase 4's
 * documented pit-stop-detection gap) can genuinely have no value yet
 * (docs/assets/02_TYPOGRAPHY_SYSTEM.md — "Empty States"). `isError` is a
 * distinct state from "no data yet": the latter means the metric
 * genuinely has no value; the former means the request failed and the
 * value is simply unknown.
 */
function KpiWidget({ title, href, linkLabel, loading, isError, value, sublabel }: KpiWidgetProps) {
  return (
    <Widget
      title={title}
      href={href}
      linkLabel={linkLabel}
      loading={loading}
      className="laptop:col-span-4"
    >
      {isError ? (
        <QueryError />
      ) : (
        <div className="flex items-baseline gap-2">
          {value ? (
            <>
              <span className="font-mono text-heading-xl text-text-primary">{value}</span>
              {sublabel ? (
                <span className="font-mono text-caption uppercase tracking-wide text-text-muted">
                  {sublabel}
                </span>
              ) : null}
            </>
          ) : (
            <>
              <span className="font-mono text-heading-xl text-text-disabled">—</span>
              <span className="font-mono text-caption uppercase tracking-wide text-text-muted">
                No data yet
              </span>
            </>
          )}
        </div>
      )}
    </Widget>
  );
}
