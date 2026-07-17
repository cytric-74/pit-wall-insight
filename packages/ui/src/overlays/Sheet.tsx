import * as DialogPrimitive from "@radix-ui/react-dialog";
import { cva, type VariantProps } from "class-variance-authority";
import { X } from "lucide-react";
import { forwardRef } from "react";
import type { HTMLAttributes } from "react";

import { cn } from "../lib/cn.js";

/**
 * "Drawers [are] reserved for supporting information. Do not replace pages
 * with drawers." (docs/assets/09_COMPONENT_STYLING.md) — a Sheet is a
 * Dialog that slides in from an edge instead of centering, built on the
 * same Radix Dialog primitive (identical focus-trap/Escape/ARIA behavior).
 */
export const Sheet = DialogPrimitive.Root;
export const SheetTrigger = DialogPrimitive.Trigger;
export const SheetClose = DialogPrimitive.Close;

const sheetVariants = cva(
  "fixed z-(--z-modal) border-border-default bg-surface-elevated p-6 shadow-dialog focus:outline-none",
  {
    variants: {
      side: {
        right: "inset-y-0 right-0 h-full w-full max-w-sm border-l",
        left: "inset-y-0 left-0 h-full w-full max-w-sm border-r",
        top: "inset-x-0 top-0 w-full border-b",
        bottom: "inset-x-0 bottom-0 w-full border-t",
      },
    },
    defaultVariants: {
      side: "right",
    },
  },
);

export interface SheetContentProps
  extends DialogPrimitive.DialogContentProps, VariantProps<typeof sheetVariants> {}

export function SheetContent({ className, side, children, ...props }: SheetContentProps) {
  return (
    <DialogPrimitive.Portal>
      <DialogPrimitive.Overlay className="fixed inset-0 z-(--z-overlay) bg-background-overlay" />
      <DialogPrimitive.Content className={cn(sheetVariants({ side }), className)} {...props}>
        {children}
        <DialogPrimitive.Close className="absolute right-4 top-4 rounded-xs text-text-muted transition-colors duration-(--duration-fast) hover:text-text-primary focus-visible:outline-none">
          <X className="size-4" aria-hidden="true" />
          <span className="sr-only">Close</span>
        </DialogPrimitive.Close>
      </DialogPrimitive.Content>
    </DialogPrimitive.Portal>
  );
}

export const SheetHeader = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("flex flex-col gap-1 pr-6", className)} {...props} />
  ),
);
SheetHeader.displayName = "SheetHeader";

export function SheetTitle({ className, ...props }: DialogPrimitive.DialogTitleProps) {
  return (
    <DialogPrimitive.Title
      className={cn("font-display text-heading-sm text-text-primary", className)}
      {...props}
    />
  );
}

export function SheetDescription({ className, ...props }: DialogPrimitive.DialogDescriptionProps) {
  return (
    <DialogPrimitive.Description
      className={cn("text-body-sm text-text-secondary", className)}
      {...props}
    />
  );
}

export const SheetFooter = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("flex items-center justify-end gap-2", className)} {...props} />
  ),
);
SheetFooter.displayName = "SheetFooter";
