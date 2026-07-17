import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes } from "react";

import { cn } from "../lib/cn.js";

/**
 * Status communication, never decoration (docs/assets/09_COMPONENT_STYLING.md
 * — "Badges": FASTEST / NEW / LIVE / RAIN / DRS / ERS, small, uppercase).
 * Semantic variants never change with the constructor theme; `constructor`
 * is the only variant that does.
 */
const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2 py-0.5 font-mono text-caption font-medium uppercase tracking-wide",
  {
    variants: {
      variant: {
        neutral: "border-border-default bg-surface-elevated text-text-secondary",
        constructor:
          "border-constructor-primary/30 bg-constructor-primary/15 text-constructor-primary",
        success: "border-success/30 bg-success/15 text-success",
        warning: "border-warning/30 bg-warning/15 text-warning",
        danger: "border-danger/30 bg-danger/15 text-danger",
        info: "border-info/30 bg-info/15 text-info",
      },
    },
    defaultVariants: {
      variant: "neutral",
    },
  },
);

export interface BadgeProps
  extends HTMLAttributes<HTMLSpanElement>, VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant, className }))} {...props} />;
}

export { badgeVariants };
