import {
  AreaChart,
  Badge,
  BarChart,
  Container,
  convertSpeed,
  getConstructorTheme,
  Hero,
  LineChart,
  Select,
  usePreferences,
  Widget,
  WidgetGrid,
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

      <Container className="flex flex-col gap-8 pb-(--section-gap)">
        <div className="flex flex-wrap items-end justify-between gap-4">
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
        </div>

        <WidgetGrid>
          <Widget
            title="Speed trace"
            description={`${driverA.abbreviation} vs ${driverB.abbreviation} — speed across the lap.`}
            className="sm:col-span-2 laptop:col-span-12"
          >
            <LineChart
              categories={DISTANCE_MARKERS}
              series={speedSeries}
              xAxisLabel="Distance"
              yAxisLabel={speedUnitLabel}
              valueFormatter={(value) => `${Math.round(value)} ${speedUnitLabel}`}
              ariaLabel={`${session.sessionName} speed trace, sample data`}
              height={360}
            />
          </Widget>

          <Widget
            title="Throttle"
            description="Throttle application across the lap."
            className="laptop:col-span-6"
          >
            <AreaChart
              categories={DISTANCE_MARKERS}
              series={channelSeries("throttle")}
              yAxisLabel="%"
              valueFormatter={(value) => `${value}%`}
              ariaLabel={`${session.sessionName} throttle trace, sample data`}
            />
          </Widget>

          <Widget
            title="Brake"
            description="Brake pressure across the lap."
            className="laptop:col-span-6"
          >
            <AreaChart
              categories={DISTANCE_MARKERS}
              series={channelSeries("brake")}
              yAxisLabel="%"
              valueFormatter={(value) => `${value}%`}
              ariaLabel={`${session.sessionName} brake trace, sample data`}
            />
          </Widget>

          <Widget
            title="Gear"
            description="Gear selection across the lap."
            className="laptop:col-span-6"
          >
            <LineChart
              categories={DISTANCE_MARKERS}
              series={channelSeries("gear")}
              yAxisLabel="Gear"
              valueFormatter={(value) => String(value)}
              ariaLabel={`${session.sessionName} gear trace, sample data`}
            />
          </Widget>

          <Widget
            title="RPM"
            description="Engine RPM across the lap."
            className="laptop:col-span-6"
          >
            <LineChart
              categories={DISTANCE_MARKERS}
              series={channelSeries("rpm")}
              yAxisLabel="RPM"
              valueFormatter={(value) => value.toLocaleString()}
              ariaLabel={`${session.sessionName} RPM trace, sample data`}
            />
          </Widget>

          <Widget
            title="Sector analysis"
            description="Sector time comparison for this lap."
            className="laptop:col-span-6"
          >
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
          </Widget>

          <Widget
            title="Session metadata"
            description="Context for this telemetry sample."
            className="laptop:col-span-6"
          >
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
          </Widget>
        </WidgetGrid>
      </Container>
    </>
  );
}
