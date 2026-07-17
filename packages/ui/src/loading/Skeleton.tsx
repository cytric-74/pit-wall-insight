import type { HTMLAttributes } from "react";

import { cn } from "../lib/cn.js";

export type SkeletonProps = HTMLAttributes<HTMLDivElement>;

/**
 * "Skeletons resemble the final layout. Avoid generic placeholders."
 * (docs/assets/09_COMPONENT_STYLING.md) — this is the raw block; compose it
 * into shapes matching the real content (e.g. a title-width bar, a card
 * outline) at the call site rather than a single generic box.
 *
 * Purely decorative (`aria-hidden`): the component using it should
 * communicate loading state to assistive tech itself (e.g. an
 * `aria-busy` region or a visually-hidden "Loading…" live region).
 */
export function Skeleton({ className, ...props }: SkeletonProps) {
  return (
    <div
      aria-hidden="true"
      className={cn(
        "animate-pulse rounded-sm bg-surface-elevated motion-reduce:animate-none",
        className,
      )}
      {...props}
    />
  );
}
