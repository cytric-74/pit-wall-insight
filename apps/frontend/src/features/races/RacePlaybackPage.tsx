import {
  AreaChart,
  Badge,
  BarChart,
  Container,
  getConstructorTheme,
  Hero,
  LineChart,
  Select,
  Widget,
  WidgetGrid,
} from "@pit-wall-insight/ui";
import { useState } from "react";

import { getSampleRace, SAMPLE_RACE_LAPS, SAMPLE_RACES } from "./data.js";

const DEFAULT_RACE_ID = SAMPLE_RACES[0]!.id;

/**
 * Race Playback (docs/assets/04_LAYOUT_SYSTEM.md — "Race Playback
 * Layout": Race Context -> Timeline -> Playback Controls -> Live
 * Analytics -> Race Events -> Driver Tracking). Runs on the sample data
 * in ./data.ts — visibly badged as such — until the race endpoints exist.
 *
 * Scope note: this implements the analytics half of that layout (position
 * changes, weather, pit stops, the event timeline, final classification).
 * The doc's "Playback Controls" — scrubbing lap-by-lap with synchronized
 * telemetry — is the flagship feature docs/13_ROADMAP.md calls out
 * separately (Milestone 7) and needs a dedicated timeline/scrubber
 * component that doesn't exist yet; it isn't attempted here.
 *
 * Each driver's line keeps their own constructor's color (per-series
 * override, same approach as Driver Dossier) rather than the global
 * theme, since a single race mixes drivers from several teams.
 */
export function RacePlaybackPage() {
  const [raceId, setRaceId] = useState<string>(DEFAULT_RACE_ID);
  const race = getSampleRace(raceId) ?? SAMPLE_RACES[0]!;
  const finalClassification = [...race.drivers].sort(
    (a, b) => a.positions[a.positions.length - 1]! - b.positions[b.positions.length - 1]!,
  );

  return (
    <>
      <Hero
        eyebrow="Race Playback"
        title={race.name}
        description={`${race.circuit} · ${race.date} · ${race.laps} laps`}
        stats={[
          { label: "Winner", value: race.stats.winner },
          { label: "Pole", value: race.stats.polePosition },
          { label: "Fastest lap", value: race.stats.fastestLap },
          { label: "Safety cars", value: String(race.stats.safetyCarLaps) },
        ]}
      />

      <Container className="flex flex-col gap-8 pb-(--section-gap)">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <Select
            label="Race"
            value={raceId}
            onValueChange={setRaceId}
            options={SAMPLE_RACES.map((item) => ({ value: item.id, label: item.name }))}
            className="min-w-64"
          />
          <Badge variant="warning">Sample data</Badge>
        </div>

        <WidgetGrid>
          <Widget
            title="Position changes"
            description="Race position after each lap — lower is better."
            className="sm:col-span-2 laptop:col-span-12"
          >
            <LineChart
              categories={SAMPLE_RACE_LAPS}
              series={race.drivers.map((driver) => {
                const teamColor = getConstructorTheme(driver.constructorId);
                return {
                  name: driver.abbreviation,
                  data: driver.positions,
                  ...(teamColor ? { color: teamColor.primary } : {}),
                };
              })}
              yAxisLabel="Position"
              yAxisInverse
              valueFormatter={(value) => `P${value}`}
              ariaLabel={`${race.name} position changes by lap, sample data`}
            />
          </Widget>

          <Widget
            title="Weather evolution"
            description="Track temperature across the race."
            className="laptop:col-span-6"
          >
            <AreaChart
              categories={SAMPLE_RACE_LAPS}
              series={[{ name: "Track temp", data: race.trackTemperature }]}
              yAxisLabel="°C"
              valueFormatter={(value) => `${value}°C`}
              ariaLabel={`${race.name} track temperature evolution, sample data`}
            />
          </Widget>

          <Widget
            title="Pit stop timeline"
            description="Stationary time per stop, in order."
            className="laptop:col-span-6"
          >
            <BarChart
              categories={race.pitStopLabels}
              series={[{ name: "Duration", data: race.pitStopDurations }]}
              yAxisLabel="Seconds"
              valueFormatter={(value) => `${value.toFixed(1)}s`}
              ariaLabel={`${race.name} pit stop durations, sample data`}
            />
          </Widget>

          <Widget
            title="Race events"
            description="Safety cars, key overtakes, and other timeline moments."
            className="laptop:col-span-6"
          >
            <ol className="flex flex-col gap-3">
              {race.events.map((event) => (
                <li key={`${event.lap}-${event.label}`} className="flex gap-3">
                  <span className="w-14 shrink-0 font-mono text-caption uppercase tracking-wide text-text-muted">
                    Lap {event.lap}
                  </span>
                  <span className="text-body-sm text-text-secondary">{event.label}</span>
                </li>
              ))}
            </ol>
          </Widget>

          <Widget
            title="Driver tracking"
            description="Final classification for this race."
            className="laptop:col-span-6"
          >
            <ol className="flex flex-col gap-2">
              {finalClassification.map((driver, index) => (
                <li
                  key={driver.abbreviation}
                  className="flex items-center justify-between border-b border-border-subtle pb-2 last:border-b-0 last:pb-0"
                >
                  <span className="flex items-center gap-3">
                    <span className="font-mono text-caption tabular-nums text-text-muted">
                      P{index + 1}
                    </span>
                    <span className="text-body-sm text-text-primary">{driver.driver}</span>
                  </span>
                  <span className="font-mono text-caption uppercase tracking-wide text-text-muted">
                    {driver.abbreviation}
                  </span>
                </li>
              ))}
            </ol>
          </Widget>
        </WidgetGrid>
      </Container>
    </>
  );
}
