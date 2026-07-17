import {
  Activity,
  CalendarRange,
  Flag,
  FlaskConical,
  MapPin,
  UserRound,
  Wrench,
} from "lucide-react";
import type { Feature } from "@pit-wall-insight/ui";

/**
 * Mission Control's Features section — one entry per analytical capability
 * area from docs/01_PRODUCT_REQUIREMENTS.md's "Core Features" (excluding
 * Dashboard/Mission Control itself and Settings, neither of which is an
 * analytical capability). Icons and routes match constants/navigation.ts
 * so the sidebar and this grid stay visually consistent.
 */
export const FEATURES: readonly Feature[] = [
  {
    title: "Driver Dossier",
    description:
      "Lap consistency, sector performance, qualifying pace, and head-to-head comparisons for every driver.",
    icon: UserRound,
    href: "/drivers",
  },
  {
    title: "Constructor Intelligence",
    description:
      "Season performance, reliability, pit stop efficiency, and strategy tendencies by team.",
    icon: Wrench,
    href: "/constructors",
  },
  {
    title: "Race Playback",
    description:
      "Lap-by-lap replay with position changes, pit stops, weather, and Safety Car timelines.",
    icon: Flag,
    href: "/races",
  },
  {
    title: "Strategy Lab",
    description:
      "Tyre degradation, undercut and overcut analysis, and stint comparison across a race.",
    icon: FlaskConical,
    href: "/strategy",
  },
  {
    title: "Telemetry Center",
    description: "Speed, throttle, brake, and gear traces with corner-by-corner comparison.",
    icon: Activity,
    href: "/telemetry",
  },
  {
    title: "Circuit Explorer",
    description: "Interactive track maps, corner data, elevation, and historical circuit records.",
    icon: MapPin,
    href: "/circuits",
  },
  {
    title: "Season Explorer",
    description: "Standings progression, team evolution, and championship battles across a season.",
    icon: CalendarRange,
    href: "/season",
  },
] as const;
