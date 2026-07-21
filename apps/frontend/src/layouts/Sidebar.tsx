import { Button, cn } from "@pit-wall-insight/ui";
import { ChevronsLeft, ChevronsRight } from "lucide-react";
import { NavLink } from "react-router";

import { NAV_ITEMS } from "../constants/navigation.js";

export interface SidebarProps {
  collapsed: boolean;
  onToggleCollapsed: () => void;
}

/**
 * "Sidebar is permanent. It represents the Control Console. Never hide
 * important navigation. Collapse only to increase workspace. Never remove
 * orientation." (docs/assets/04_LAYOUT_SYSTEM.md)
 *
 * Responsive approach: below the `laptop:` breakpoint the sidebar is
 * always icon-only (docs/assets/04 — "Small Displays: reduce complexity,
 * never reduce clarity"); the manual collapse toggle only appears at
 * `laptop:` and above, where there's a meaningful expanded state to
 * collapse from. A full mobile overlay/drawer pattern is a reasonable
 * future addition but out of scope for this shell.
 */
export function Sidebar({ collapsed, onToggleCollapsed }: SidebarProps) {
  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-(--z-sidebar) flex w-(--sidebar-collapsed) flex-col border-r border-border-default bg-surface-primary transition-[width] duration-(--duration-panel) ease-standard",
        !collapsed && "laptop:w-(--sidebar-width)",
      )}
    >
      <div className="flex h-16 shrink-0 items-center justify-center px-4 laptop:justify-start">
        <span
          className={cn(
            "truncate font-display text-heading-sm text-text-primary",
            collapsed ? "hidden" : "hidden laptop:inline",
          )}
        >
          Pit Wall Insight
        </span>
        <span
          className={cn(
            "font-display text-heading-sm text-text-primary",
            !collapsed && "laptop:hidden",
          )}
        >
          PW
        </span>
      </div>

      <nav className="flex flex-1 flex-col gap-1 overflow-y-auto px-2 py-4" aria-label="Primary">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.href}
            to={item.href}
            end={item.href === "/"}
            data-cursor="button"
            className={({ isActive }) =>
              cn(
                "flex items-center justify-center gap-3 rounded-md border-l-2 border-transparent px-3 py-2 font-body text-body-sm text-text-secondary transition-colors duration-(--duration-fast) ease-standard hover:bg-surface-hover hover:text-text-primary",
                !collapsed && "laptop:justify-start",
                isActive && "border-constructor-primary bg-surface-hover text-text-primary",
              )
            }
          >
            <item.icon className="size-5 shrink-0" aria-hidden="true" />
            <span className={cn("truncate", collapsed ? "hidden" : "hidden laptop:inline")}>
              {item.label}
            </span>
          </NavLink>
        ))}
      </nav>

      <div className="hidden shrink-0 border-t border-border-default p-2 laptop:flex">
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggleCollapsed}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          className="mx-auto"
        >
          {collapsed ? (
            <ChevronsRight className="size-4" aria-hidden="true" />
          ) : (
            <ChevronsLeft className="size-4" aria-hidden="true" />
          )}
        </Button>
      </div>
    </aside>
  );
}
