import {
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

import { getSampleDriver, SAMPLE_DRIVERS, SAMPLE_ROUNDS, SAMPLE_STINT_LAPS } from "./data.js";

const DEFAULT_DRIVER_ID = SAMPLE_DRIVERS[0]!.id;

/**
 * Driver Dossier (docs/assets/04_LAYOUT_SYSTEM.md — "Driver Dossier
 * Layout": Driver Overview -> Performance Summary -> Lap Analysis ->
 * Telemetry -> Race History -> Comparisons). Runs entirely on the sample
 * data in ./data.ts — a visible "Sample data" badge says so — until the
 * driver endpoints exist.
 *
 * Charts are colored with the *selected driver's* constructor colors
 * (explicit per-series override) rather than the global constructor
 * theme, so comparing drivers across teams always shows each driver in
 * their own team's color regardless of which theme the user picked.
 */
export function DriverDossierPage() {
  const [driverId, setDriverId] = useState<string>(DEFAULT_DRIVER_ID);
  const driver = getSampleDriver(driverId) ?? SAMPLE_DRIVERS[0]!;
  const teamColors = getConstructorTheme(driver.constructorId);
  // Absent (not `undefined`) when the lookup misses, so charts fall back
  // to the active constructor theme rather than receiving color: undefined.
  const primaryColor = teamColors ? { color: teamColors.primary } : {};
  const secondaryColor = teamColors ? { color: teamColors.secondary } : {};

  return (
    <>
      <Hero
        eyebrow="Driver Dossier"
        title={driver.name}
        description={`#${driver.number} · ${driver.teamName} · ${driver.nationality}`}
        stats={[
          { label: "Wins", value: String(driver.stats.wins) },
          { label: "Podiums", value: String(driver.stats.podiums) },
          { label: "Poles", value: String(driver.stats.poles) },
          { label: "Fastest laps", value: String(driver.stats.fastestLaps) },
        ]}
      />

      <Container className="flex flex-col gap-8 pb-(--section-gap)">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <Select
            label="Driver"
            value={driverId}
            onValueChange={setDriverId}
            options={SAMPLE_DRIVERS.map((item) => ({
              value: item.id,
              label: `${item.abbreviation} — ${item.name}`,
            }))}
            className="min-w-64"
          />
          <Badge variant="warning">Sample data</Badge>
        </div>

        <WidgetGrid>
          <Widget
            title="Race pace"
            description={`Stint lap times vs. ${driver.teammateName.toLowerCase()} — lower is faster.`}
            className="sm:col-span-2 laptop:col-span-12"
          >
            <LineChart
              categories={SAMPLE_STINT_LAPS}
              series={[
                { name: driver.abbreviation, data: driver.racePace, ...primaryColor },
                { name: driver.teammateName, data: driver.teammatePace, ...secondaryColor },
              ]}
              yAxisLabel="Lap time (s)"
              valueFormatter={(value) => `${value.toFixed(1)}s`}
              ariaLabel={`${driver.name} race pace compared with teammate, sample data`}
            />
          </Widget>

          <Widget
            title="Qualifying vs. race"
            description="Grid position against finishing position by round — lower is better."
            className="laptop:col-span-6"
          >
            <BarChart
              categories={SAMPLE_ROUNDS}
              series={[
                { name: "Qualifying", data: driver.qualifyingPositions, ...secondaryColor },
                { name: "Race", data: driver.racePositions, ...primaryColor },
              ]}
              yAxisLabel="Position"
              valueFormatter={(value) => `P${value}`}
              ariaLabel={`${driver.name} qualifying versus race positions, sample data`}
            />
          </Widget>

          <Widget
            title="Position progression"
            description="Finishing position across the season — lower is better."
            className="laptop:col-span-6"
          >
            <LineChart
              categories={SAMPLE_ROUNDS}
              series={[{ name: driver.abbreviation, data: driver.racePositions, ...primaryColor }]}
              yAxisLabel="Finish"
              valueFormatter={(value) => `P${value}`}
              ariaLabel={`${driver.name} finishing position progression, sample data`}
            />
          </Widget>

          <Widget
            title="Telemetry"
            description="Speed, throttle, and brake traces"
            href="/telemetry"
            linkLabel="Telemetry Center"
            loading
            className="sm:col-span-2 laptop:col-span-12"
          />
        </WidgetGrid>
      </Container>
    </>
  );
}
