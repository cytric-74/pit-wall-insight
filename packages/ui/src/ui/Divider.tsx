import type { HTMLAttributes } from "react";

import { cn } from "../lib/cn.js";

export interface DividerProps extends HTMLAttributes<HTMLDivElement> {
  orientation?: "horizontal" | "vertical";
}

/**
 * "Used sparingly. Whitespace is preferred." (docs/assets/09_COMPONENT_STYLING.md)
 * Renders as a real `separator` for assistive technology rather than a bare
 * `<hr>`-lookalike div with no semantics.
 */
export function Divider({ className, orientation = "horizontal", ...props }: DividerProps) {
  return (
    <div
      role="separator"
      aria-orientation={orientation}
      className={cn(
        "shrink-0 bg-border-subtle",
        orientation === "horizontal" ? "h-px w-full" : "h-full w-px",
        className,
      )}
      {...props}
    />
  );
}
