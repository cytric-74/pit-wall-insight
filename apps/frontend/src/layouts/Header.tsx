import { Button } from "@pit-wall-insight/ui";
import { Search } from "lucide-react";
import { useLocation } from "react-router";

import { NAV_ITEMS } from "../constants/navigation.js";
import { ConstructorSwitcher } from "./ConstructorSwitcher.js";

export interface HeaderProps {
  onOpenCommandPalette: () => void;
}

/**
 * "Top Navigation: Reserved for Context, Global Actions, Session
 * Information. Keep uncluttered." (docs/assets/09_COMPONENT_STYLING.md)
 * No session information yet — nothing is selected until real content
 * exists (out of scope for this shell).
 */
export function Header({ onOpenCommandPalette }: HeaderProps) {
  const location = useLocation();
  const activeItem = NAV_ITEMS.find((item) =>
    item.href === "/" ? location.pathname === "/" : location.pathname.startsWith(item.href),
  );

  return (
    <header className="sticky top-0 z-(--z-header) flex h-16 shrink-0 items-center justify-between border-b border-border-default bg-background-primary px-6">
      <span className="font-mono text-caption uppercase tracking-wide text-text-muted">
        {activeItem?.label ?? "Pit Wall Insight"}
      </span>

      <div className="flex items-center gap-3">
        <Button variant="secondary" size="sm" onClick={onOpenCommandPalette} className="gap-2">
          <Search className="size-4" aria-hidden="true" />
          <span className="hidden sm:inline">Search</span>
          <kbd className="ml-1 hidden rounded-xs border border-border-default bg-surface-elevated px-1.5 py-0.5 font-mono text-caption text-text-muted sm:inline">
            Ctrl K
          </kbd>
        </Button>
        <ConstructorSwitcher hideLabel />
      </div>
    </header>
  );
}
