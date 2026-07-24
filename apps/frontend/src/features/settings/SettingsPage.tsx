import {
  Container,
  Hero,
  Select,
  Switch,
  Section,
  isConstructorId,
  usePreferences,
  usePrefersReducedMotion,
  useConstructorTheme,
  type SpeedUnit,
  type TemperatureUnit,
} from "@pit-wall-insight/ui";

const DEFAULT_THEME_OPTION = "default";

const SPEED_UNIT_OPTIONS: readonly { value: SpeedUnit; label: string }[] = [
  { value: "kph", label: "Kilometers per hour (km/h)" },
  { value: "mph", label: "Miles per hour (mph)" },
];

const TEMPERATURE_UNIT_OPTIONS: readonly { value: TemperatureUnit; label: string }[] = [
  { value: "celsius", label: "Celsius (°C)" },
  { value: "fahrenheit", label: "Fahrenheit (°F)" },
];

/**
 * Settings (docs/04_FRONTEND_ARCHITECTURE.md lists `settings/` as the
 * final stop in the routing flow). No dedicated "Settings Layout"
 * section exists in docs/assets/04_LAYOUT_SYSTEM.md, so this follows
 * the generic page rhythm every other page uses (Hero -> grouped
 * panels) rather than a documented step order.
 *
 * Rebuilt using the unboxed `Section` composition to let settings form
 * elements float natively. High Contrast and Reduced Motion toggles are
 * paired in a two-column system layout.
 *
 * Appearance reuses the existing constructor theme picker rather than
 * introducing a light/dark toggle — docs/03_DESIGN_SYSTEM.md Engineering
 * Decision 001 is "Dark Mode Only," so the one personalization axis this
 * product actually has is which constructor's colors are active.
 */
export function SettingsPage() {
  const { constructorId, constructors, setConstructor } = useConstructorTheme();
  const { preferences, setSpeedUnit, setTemperatureUnit, setMotion, setHighContrast } =
    usePreferences();
  const reducedMotionActive = usePrefersReducedMotion();

  return (
    <>
      <Hero
        eyebrow="Settings"
        title="Preferences"
        description="Appearance, telemetry units, and accessibility — saved to this device."
      />

      <Container className="flex flex-col gap-16 pb-(--section-gap)">
        <Section
          title="Appearance"
          description="The active constructor accent, used across every chart and panel."
        >
          <Select
            label="Constructor theme"
            value={constructorId ?? DEFAULT_THEME_OPTION}
            onValueChange={(value) => {
              setConstructor(isConstructorId(value) ? value : null);
            }}
            options={[
              { value: DEFAULT_THEME_OPTION, label: "Default (Pit Wall red)" },
              ...constructors.map((team) => ({ value: team.id, label: team.name })),
            ]}
            className="max-w-sm"
          />
        </Section>

        <Section
          title="Telemetry units"
          description="Applied to speed and temperature readouts across the platform."
        >
          <div className="flex flex-col gap-4">
            <Select
              label="Speed"
              value={preferences.speedUnit}
              onValueChange={(value) => {
                setSpeedUnit(value as SpeedUnit);
              }}
              options={SPEED_UNIT_OPTIONS}
              className="max-w-sm"
            />
            <Select
              label="Temperature"
              value={preferences.temperatureUnit}
              onValueChange={(value) => {
                setTemperatureUnit(value as TemperatureUnit);
              }}
              options={TEMPERATURE_UNIT_OPTIONS}
              className="max-w-sm"
            />
          </div>
        </Section>

        <Section
          title="System preferences"
          description="Contrast settings and motion controls for the user interface."
        >
          <div className="grid grid-cols-1 gap-12 laptop:grid-cols-2">
            <div className="flex flex-col gap-4">
              <h3 className="font-mono text-caption uppercase tracking-wide text-text-muted">
                Accessibility
              </h3>
              <Switch
                label="High contrast"
                description="Uses the existing palette's stronger tones — no new colors."
                checked={preferences.highContrast}
                onCheckedChange={setHighContrast}
              />
            </div>

            <div className="flex flex-col gap-4">
              <h3 className="font-mono text-caption uppercase tracking-wide text-text-muted">
                Animation
              </h3>
              <Switch
                label="Reduce motion"
                description={
                  reducedMotionActive
                    ? "Motion is currently reduced."
                    : "Motion is currently at full effect."
                }
                checked={preferences.motion === "reduced"}
                onCheckedChange={(checked) => {
                  setMotion(checked ? "reduced" : "system");
                }}
              />
            </div>
          </div>
        </Section>
      </Container>
    </>
  );
}
