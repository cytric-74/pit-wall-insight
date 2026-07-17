import { forwardRef } from "react";
import type { HTMLAttributes } from "react";

import { cn } from "../lib/cn.js";

export type ContainerProps = HTMLAttributes<HTMLDivElement>;

/**
 * Centers content and caps it at the documented content width
 * (docs/03_DESIGN_SYSTEM.md — Grid: "Content Width 1440px"). Large
 * monitors get more breathing room, not longer lines
 * (docs/assets/04_LAYOUT_SYSTEM.md — "Content Width").
 */
export const Container = forwardRef<HTMLDivElement, ContainerProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("mx-auto w-full max-w-(--content-width) px-6", className)}
      {...props}
    />
  ),
);
Container.displayName = "Container";
