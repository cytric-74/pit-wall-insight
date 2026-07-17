import { forwardRef } from "react";
import type { HTMLAttributes } from "react";

import { cn } from "../lib/cn.js";

export interface SurfaceProps extends HTMLAttributes<HTMLDivElement> {
  /** Uses the elevated surface + panel shadow (docs/03_DESIGN_SYSTEM.md "Elevated Surface"). */
  elevated?: boolean;
}

/**
 * The base "box" primitive — background, border, radius. Every other
 * container (Card, Dialog, Sheet, dropdown menus) is built on top of this
 * rather than repeating the same three properties everywhere.
 */
export const Surface = forwardRef<HTMLDivElement, SurfaceProps>(
  ({ className, elevated = false, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "rounded-lg border border-border-default",
        elevated ? "bg-surface-elevated shadow-panel" : "bg-surface-primary",
        className,
      )}
      {...props}
    />
  ),
);
Surface.displayName = "Surface";
