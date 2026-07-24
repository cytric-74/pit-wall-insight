import {
  AreaChart,
  Badge,
  BarChart,
  Container,
  convertSpeed,
  getConstructorTheme,
  Hero,
  LineChart,
  Section,
  Select,
  usePreferences,
} from "@pit-wall-insight/ui";
import { useState } from "react";

import { DISTANCE_MARKERS, getSampleSession, SAMPLE_TELEMETRY_SESSIONS } from "./data.js";

const DEFAULT_SESSION_ID = SAMPLE_TELEMETRY_SESSIONS[0]!.id;

/**
 * Telemetry Center (docs/assets/04_LAYOUT_SYSTEM.md — "Telemetry Center
 * Layout": Session Context -> Telemetry Viewer -> Sector Analysis ->
 * Speed Trace -> Throttle -> Brake -> Gear -> Metadata. "Telemetry
 * always occupies the largest visual area."). Runs on the sample data
 * in ./data.ts — visibly badged as such — until the telemetry endpoints
 * (`fct_telemetry`) exist.
 *
 * Editorial rebuild: "Speed trace" is the one primary, full-width focus.
 * Throttle/brake/gear/RPM stay full channel traces rather than becoming
 * `InstrumentGauge` single-value readouts — collapsing a whole lap's
 * throttle profile into one number would lose exactly the thing this page
 * exists to show (*where* on track it changes, not just an average), so
 * fidelity to the data wins over mechanically applying the gauge
 * treatment everywhere. They're demoted instead by being paired into two
 * secondary two-column sections (throttle+brake, gear+RPM) beneath the
 * primary trace, plus a third pairing sector analysis with session
 * metadata — never five-plus equal-weight boxes.
 *
 * Scope note: docs/01_PRODUCT_REQUIREMENTS.md also lists "Racing line
 * comparison" and "Corner analysis" for this page — both need the
 * per-sample x/y/z track position `fct_telemetry` carries, which the
 * sample data here doesn't model. Not attempted; this covers the
 * channel traces (speed, throttle, brake, gear, RPM) and sector deltas.
 *
 * Two drivers per session, matching "Comparison Mode"
 * (docs/assets/06_CHART_DESIGN_SYSTEM.md): the first driver's line uses
 * their constructor color, the second falls back to the chart theme's
 * neutral secondary tone rather than their own team color.
 *
 * Speed is stored in km/h and converted at render time via the
 * Settings page's speed-unit preference (`usePreferences`).
 */
export function TelemetryViewerPage() {
  const [sessionId, setSessionId] = useState<string>(DEFAULT_SESSION_ID);
  const session = getSampleSession(sessionId) ?? SAMPLE_TELEMETRY_SESSIONS[0]!;
  const [driverA, driverB] = session.drivers;
  const driverATheme = getConstructorTheme(driverA.constructorId);
  const { preferences } = usePreferences();
  const speedUnitLabel = preferences.speedUnit === "mph" ? "mph" : "km/h";

  const channelSeries = (channel: "throttle" | "brake" | "rpm" | "gear") => [
    {
      name: driverA.abbreviation,
      data: driverA[channel],
      ...(driverATheme ? { color: driverATheme.primary } : {}),
    },
    { name: driverB.abbreviation, data: driverB[channel] },
  ];

  const speedSeries = [
    {
      name: driverA.abbreviation,
      data: driverA.speed.map((value) => convertSpeed(value, preferences.speedUnit)),
      ...(driverATheme ? { color: driverATheme.primary } : {}),
    },
    {
      name: driverB.abbreviation,
      data: driverB.speed.map((value) => convertSpeed(value, preferences.speedUnit)),
    },
  ];

  return (
    <>
      <Hero
        eyebrow="Telemetry Center"
        title={`${session.sessionName} · ${session.circuit}`}
        description={`${driverA.driver} vs ${driverB.driver} · Lap ${session.lapNumber} · ${session.compound}`}
        stats={[
          {
            label: "Top speed",
            value: String(
              Math.round(convertSpeed(session.summary.topSpeed, preferences.speedUnit)),
            ),
            unit: speedUnitLabel,
          },
          { label: "Avg throttle", value: String(session.summary.averageThrottle), unit: "%" },
          { label: "Avg brake", value: String(session.summary.averageBrake), unit: "%" },
          { label: "Top RPM", value: session.summary.topRpm.toLocaleString() },
        ]}
      />

      <Container className="flex flex-wrap items-end justify-between gap-4 py-8">
        <Select
          label="Session"
          value={sessionId}
          onValueChange={setSessionId}
          options={SAMPLE_TELEMETRY_SESSIONS.map((item) => ({
            value: item.id,
            label: `${item.circuit} — ${item.sessionName}`,
          }))}
          className="min-w-72"
        />
        <Badge variant="warning">Sample data</Badge>
      </Container>

      <Section
        title="Speed trace"
        description={`${driverA.abbreviation} vs ${driverB.abbreviation} — speed across the lap.`}
      >
        <LineChart
          categories={DISTANCE_MARKERS}
          series={speedSeries}
          xAxisLabel="Distance"
          yAxisLabel={speedUnitLabel}
          valueFormatter={(value) => `${Math.round(value)} ${speedUnitLabel}`}
          ariaLabel={`${session.sessionName} speed trace, sample data`}
          height={400}
        />
      </Section>

      <Section title="Throttle & brake" description="Pedal application across the lap.">
        <div className="grid grid-cols-1 gap-x-16 gap-y-10 laptop:grid-cols-2">
          <div className="flex flex-col gap-4">
            <h3 className="font-mono text-caption uppercase tracking-wide text-text-muted">
              Throttle
            </h3>
            <AreaChart
              categories={DISTANCE_MARKERS}
              series={channelSeries("throttle")}
              yAxisLabel="%"
              valueFormatter={(value) => `${value}%`}
              ariaLabel={`${session.sessionName} throttle trace, sample data`}
            />
          </div>
          <div className="flex flex-col gap-4">
            <h3 className="font-mono text-caption uppercase tracking-wide text-text-muted">
              Brake
            </h3>
            <AreaChart
              categories={DISTANCE_MARKERS}
              series={channelSeries("brake")}
              yAxisLabel="%"
              valueFormatter={(value) => `${value}%`}
              ariaLabel={`${session.sessionName} brake trace, sample data`}
            />
          </div>
        </div>
      </Section>

      <Section title="Gear & RPM" description="Powertrain response across the lap.">
        <div className="grid grid-cols-1 gap-x-16 gap-y-10 laptop:grid-cols-2">
          <div className="flex flex-col gap-4">
            <h3 className="font-mono text-caption uppercase tracking-wide text-text-muted">Gear</h3>
            <LineChart
              categories={DISTANCE_MARKERS}
              series={channelSeries("gear")}
              yAxisLabel="Gear"
              valueFormatter={(value) => String(value)}
              ariaLabel={`${session.sessionName} gear trace, sample data`}
            />
          </div>
          <div className="flex flex-col gap-4">
            <h3 className="font-mono text-caption uppercase tracking-wide text-text-muted">RPM</h3>
            <LineChart
              categories={DISTANCE_MARKERS}
              series={channelSeries("rpm")}
              yAxisLabel="RPM"
              valueFormatter={(value) => value.toLocaleString()}
              ariaLabel={`${session.sessionName} RPM trace, sample data`}
            />
          </div>
        </div>
      </Section>

      <Section title="Lap detail" description="Sector time comparison and session context.">
        <div className="grid grid-cols-1 gap-x-16 gap-y-10 laptop:grid-cols-2">
          <div className="flex flex-col gap-4">
            <h3 className="font-mono text-caption uppercase tracking-wide text-text-muted">
              Sector analysis
            </h3>
            <BarChart
              categories={session.sectors.map((sector) => sector.sector)}
              series={[
                {
                  name: driverA.abbreviation,
                  data: session.sectors.map((sector) => sector.times[driverA.abbreviation] ?? 0),
                  ...(driverATheme ? { color: driverATheme.primary } : {}),
                },
                {
                  name: driverB.abbreviation,
                  data: session.sectors.map((sector) => sector.times[driverB.abbreviation] ?? 0),
                },
              ]}
              yAxisLabel="Seconds"
              valueFormatter={(value) => `${value.toFixed(3)}s`}
              ariaLabel={`${session.sessionName} sector time comparison, sample data`}
            />
          </div>
          <div className="flex flex-col gap-4">
            <h3 className="font-mono text-caption uppercase tracking-wide text-text-muted">
              Session metadata
            </h3>
            <ol className="flex flex-col gap-2">
              {[
                { label: "Circuit", value: session.circuit },
                { label: "Lap", value: String(session.lapNumber) },
                { label: "Compound", value: session.compound },
                { label: "Drivers", value: `${driverA.abbreviation} / ${driverB.abbreviation}` },
              ].map((row) => (
                <li
                  key={row.label}
                  className="flex items-center justify-between border-b border-border-subtle pb-2 last:border-b-0 last:pb-0"
                >
                  <span className="text-caption uppercase tracking-wide text-text-muted">
                    {row.label}
                  </span>
                  <span className="text-body-sm text-text-primary">{row.value}</span>
                </li>
              ))}
            </ol>
          </div>
        </div>
      </Section>
    </>
  );
}
