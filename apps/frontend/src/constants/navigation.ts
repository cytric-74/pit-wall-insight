import {
  Activity,
  CalendarRange,
  Flag,
  FlaskConical,
  LayoutDashboard,
  MapPin,
  Settings,
  UserRound,
  Wrench,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

/**
 * Primary navigation. Labels follow the documented product vocabulary
 * (docs/assets/01_VISUAL_LANGUAGE.md — "Product Vocabulary": prefer
 * "Mission Control" over "Dashboard", "Driver Dossier" over "Drivers",
 * etc.) rather than generic dashboard terminology.
 *
 * Routes exist so navigation has somewhere real to go; each currently
 * renders a placeholder (see routes/RouteholderPage.tsx) — no analytics
 * content yet.
 */
export interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
}

export const NAV_ITEMS: readonly NavItem[] = [
  { label: "Mission Control", href: "/", icon: LayoutDashboard },
  { label: "Driver Dossier", href: "/drivers", icon: UserRound },
  { label: "Constructor Intelligence", href: "/constructors", icon: Wrench },
  { label: "Race Playback", href: "/races", icon: Flag },
  { label: "Strategy Lab", href: "/strategy", icon: FlaskConical },
  { label: "Telemetry Center", href: "/telemetry", icon: Activity },
  { label: "Circuit Explorer", href: "/circuits", icon: MapPin },
  { label: "Season Explorer", href: "/season", icon: CalendarRange },
  { label: "Settings", href: "/settings", icon: Settings },
] as const;
