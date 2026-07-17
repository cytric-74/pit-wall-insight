import { Dashboard, Features, Hero, Statistics, Widget, WidgetGrid } from "@pit-wall-insight/ui";

import { FEATURES } from "../constants/features.js";
import { STATISTICS } from "../constants/statistics.js";

/**
 * Only the Hero, Features, Statistics, and Dashboard sections — no real
 * standings/race data or charts yet (out of scope for this task).
 */
export function MissionControlPage() {
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
        description="Current season, driver and constructor standings, and the latest race — once the analytics API is wired up."
      >
        <WidgetGrid>
          <Widget
            title="Season overview"
            description="Current season progress"
            href="/season"
            linkLabel="Season Explorer"
            loading
            className="sm:col-span-2 laptop:col-span-12"
          />
          <Widget
            title="Driver standings"
            description="Championship order"
            href="/drivers"
            linkLabel="Driver Dossier"
            loading
            className="laptop:col-span-6"
          />
          <Widget
            title="Constructor standings"
            description="Championship order"
            href="/constructors"
            linkLabel="Constructor Intelligence"
            loading
            className="laptop:col-span-6"
          />
          <KpiWidget title="Fastest lap" href="/telemetry" linkLabel="Telemetry Center" />
          <KpiWidget title="Avg. pit stop" href="/strategy" linkLabel="Strategy Lab" />
          <KpiWidget title="Overtakes" href="/races" linkLabel="Race Playback" />
          <Widget
            title="Recent race summary"
            description="Latest completed round"
            href="/races"
            linkLabel="Race Playback"
            loading
            className="sm:col-span-2 laptop:col-span-12"
          />
        </WidgetGrid>
      </Dashboard>
    </>
  );
}

interface KpiWidgetProps {
  title: string;
  href: string;
  linkLabel: string;
}

/**
 * A single-value KPI tile. Not wired to real data yet, so it shows an
 * explicit "no data" state rather than a fabricated number
 * (docs/assets/02_TYPOGRAPHY_SYSTEM.md — "Empty States": terse, technical
 * language, e.g. "NO TELEMETRY AVAILABLE", never conversational).
 */
function KpiWidget({ title, href, linkLabel }: KpiWidgetProps) {
  return (
    <Widget title={title} href={href} linkLabel={linkLabel} className="laptop:col-span-4">
      <div className="flex items-baseline gap-2">
        <span className="font-mono text-heading-xl text-text-disabled">—</span>
        <span className="font-mono text-caption uppercase tracking-wide text-text-muted">
          No data yet
        </span>
      </div>
    </Widget>
  );
}
