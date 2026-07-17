import * as DialogPrimitive from "@radix-ui/react-dialog";
import { X } from "lucide-react";
import { forwardRef } from "react";
import type { HTMLAttributes } from "react";

import { cn } from "../lib/cn.js";

/**
 * "Dialogs interrupt workflows. Use only when necessary. Background fades.
 * Focus shifts." (docs/assets/09_COMPONENT_STYLING.md)
 *
 * Built on Radix Dialog, which already provides: focus trap, Escape to
 * close, `aria-modal`, automatic `aria-labelledby`/`aria-describedby` wiring
 * from DialogTitle/DialogDescription, and focus return to the trigger on
 * close — see docs/assets/13_ACCESSIBILITY_VISUALS.md's Dialog/keyboard
 * requirements.
 */
export const Dialog = DialogPrimitive.Root;
export const DialogTrigger = DialogPrimitive.Trigger;
export const DialogClose = DialogPrimitive.Close;

export function DialogContent({
  className,
  children,
  ...props
}: DialogPrimitive.DialogContentProps) {
  return (
    <DialogPrimitive.Portal>
      <DialogPrimitive.Overlay className="fixed inset-0 z-(--z-overlay) bg-background-overlay" />
      <DialogPrimitive.Content
        className={cn(
          "fixed left-1/2 top-1/2 z-(--z-modal) w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-lg border border-border-default bg-surface-elevated p-6 shadow-dialog focus:outline-none",
          className,
        )}
        {...props}
      >
        {children}
        <DialogPrimitive.Close className="absolute right-4 top-4 rounded-xs text-text-muted transition-colors duration-(--duration-fast) hover:text-text-primary focus-visible:outline-none">
          <X className="size-4" aria-hidden="true" />
          <span className="sr-only">Close</span>
        </DialogPrimitive.Close>
      </DialogPrimitive.Content>
    </DialogPrimitive.Portal>
  );
}

export const DialogHeader = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("flex flex-col gap-1 pr-6", className)} {...props} />
  ),
);
DialogHeader.displayName = "DialogHeader";

export function DialogTitle({ className, ...props }: DialogPrimitive.DialogTitleProps) {
  return (
    <DialogPrimitive.Title
      className={cn("font-display text-heading-sm text-text-primary", className)}
      {...props}
    />
  );
}

export function DialogDescription({ className, ...props }: DialogPrimitive.DialogDescriptionProps) {
  return (
    <DialogPrimitive.Description
      className={cn("text-body-sm text-text-secondary", className)}
      {...props}
    />
  );
}

export const DialogFooter = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("flex items-center justify-end gap-2", className)} {...props} />
  ),
);
DialogFooter.displayName = "DialogFooter";
