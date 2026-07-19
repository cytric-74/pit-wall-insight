import type { SpeedUnit, TemperatureUnit } from "../theme/preferences-provider.js";

/** Telemetry and weather values are stored in km/h and °C; converted only at display time. */
export function convertSpeed(kph: number, unit: SpeedUnit): number {
  return unit === "mph" ? kph * 0.621371 : kph;
}

export function formatSpeed(kph: number, unit: SpeedUnit): string {
  return `${Math.round(convertSpeed(kph, unit))} ${unit === "mph" ? "mph" : "km/h"}`;
}

export function convertTemperature(celsius: number, unit: TemperatureUnit): number {
  return unit === "fahrenheit" ? (celsius * 9) / 5 + 32 : celsius;
}

export function formatTemperature(celsius: number, unit: TemperatureUnit): string {
  return `${Math.round(convertTemperature(celsius, unit))}°${unit === "fahrenheit" ? "F" : "C"}`;
}
