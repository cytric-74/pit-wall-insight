import { Container, Divider, StatusDot } from "@pit-wall-insight/ui";
import { NavLink } from "react-router";

import { NAV_ITEMS, type NavItem } from "../constants/navigation.js";

// Mission Control (index 0) is excluded — it's the page these links live on.
const ANALYTICS_LINKS = NAV_ITEMS.slice(1, 5);
const EXPLORE_LINKS = NAV_ITEMS.slice(5);

const CURRENT_YEAR = new Date().getFullYear();

/**
 * Persistent site footer (docs/04_FRONTEND_ARCHITECTURE.md — every page's
 * rhythm ends with Footer). It's chrome, not page content, so — like
 * Header/Sidebar — it renders statically with no scroll-reveal animation.
 *
 * Uses the same `Container` as Hero/Features/Statistics so its columns
 * stay aligned with everything above it, and reuses `StatusDot` (Hero's
 * "Nothing Design" accent-dot motif) so the same telemetry-status
 * vocabulary appears consistently at both ends of the page.
 */
export function Footer() {
  return (
    <footer className="shrink-0 border-t border-border-default">
      <Container className="flex flex-col gap-10 py-12">
        <div className="grid gap-10 sm:grid-cols-[minmax(0,1fr)_auto_auto]">
          <div className="flex max-w-sm flex-col gap-3">
            <span className="font-display text-heading-sm text-text-primary">Pit Wall Insight</span>
            <p className="text-body-sm text-text-secondary">
              Formula One telemetry, strategy, and race intelligence in one engineering-grade
              analytics platform.
            </p>
            <div className="flex items-center gap-2">
              <StatusDot />
              <span className="font-mono text-caption uppercase tracking-telemetry text-text-muted">
                Systems nominal
              </span>
            </div>
          </div>

          <FooterLinkGroup heading="Analytics" items={ANALYTICS_LINKS} />
          <FooterLinkGroup heading="Explore" items={EXPLORE_LINKS} />
        </div>

        <Divider />

        <div className="flex flex-col gap-2 font-mono text-caption text-text-muted sm:flex-row sm:items-center sm:justify-between">
          <span>© {CURRENT_YEAR} Pit Wall Insight</span>
          <span>v0.1.0</span>
        </div>
      </Container>
    </footer>
  );
}

interface FooterLinkGroupProps {
  heading: string;
  items: readonly NavItem[];
}

function FooterLinkGroup({ heading, items }: FooterLinkGroupProps) {
  return (
    <nav aria-label={heading} className="flex flex-col gap-3">
      <span
        aria-hidden="true"
        className="font-mono text-caption uppercase tracking-wide text-text-muted"
      >
        {heading}
      </span>
      <ul className="flex flex-col gap-2">
        {items.map((item) => (
          <li key={item.href}>
            <NavLink
              to={item.href}
              className="text-body-sm text-text-secondary transition-colors duration-(--duration-fast) ease-standard hover:text-text-primary"
            >
              {item.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}
