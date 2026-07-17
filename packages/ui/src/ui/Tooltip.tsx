import * as TooltipPrimitive from "@radix-ui/react-tooltip";
import type { ReactNode } from "react";

import { cn } from "../lib/cn.js";

/**
 * Tooltips answer "What am I looking at?" — nothing more
 * (docs/assets/09_COMPONENT_STYLING.md — "Tooltips"). Content uses
 * monospaced typography per the same doc.
 *
 * Wrap the application once in `<TooltipProvider>` so every `<Tooltip>`
 * shares one delay group.
 */
export const TooltipProvider = TooltipPrimitive.Provider;

export interface TooltipProps {
  content: ReactNode;
  children: ReactNode;
  side?: "top" | "right" | "bottom" | "left";
  className?: string;
}

export function Tooltip({ content, children, side = "top", className }: TooltipProps) {
  return (
    <TooltipPrimitive.Root delayDuration={200}>
      <TooltipPrimitive.Trigger asChild>{children}</TooltipPrimitive.Trigger>
      <TooltipPrimitive.Portal>
        <TooltipPrimitive.Content
          side={side}
          sideOffset={6}
          className={cn(
            "z-(--z-tooltip) rounded-sm border border-border-default bg-surface-elevated px-3 py-1.5 font-mono text-caption text-text-primary shadow-md",
            className,
          )}
        >
          {content}
          <TooltipPrimitive.Arrow className="fill-surface-elevated" />
        </TooltipPrimitive.Content>
      </TooltipPrimitive.Portal>
    </TooltipPrimitive.Root>
  );
}
