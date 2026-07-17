import * as SelectPrimitive from "@radix-ui/react-select";
import { Check, ChevronDown, CircleAlert } from "lucide-react";
import { useId } from "react";

import { cn } from "../lib/cn.js";

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectProps {
  label: string;
  /** Keeps the label programmatically associated (for assistive tech) but visually hidden — for compact contexts like a toolbar. */
  hideLabel?: boolean;
  description?: string;
  error?: string;
  placeholder?: string;
  options: readonly SelectOption[];
  value?: string;
  defaultValue?: string;
  onValueChange?: (value: string) => void;
  disabled?: boolean;
  required?: boolean;
  name?: string;
  className?: string;
}

/**
 * "Dropdowns should resemble engineering controls. Minimal transitions.
 * Clear hierarchy... All selectors should follow identical interaction
 * patterns." (docs/assets/09_COMPONENT_STYLING.md)
 *
 * Wraps Radix Select (listbox semantics, roving focus, typeahead) behind
 * the same label/description/error prop shape as Input/Textarea, so every
 * form control in this package is used the same way.
 */
export function Select({
  label,
  hideLabel = false,
  description,
  error,
  placeholder = "Select…",
  options,
  value,
  defaultValue,
  onValueChange,
  disabled,
  required,
  name,
  className,
}: SelectProps) {
  const generatedId = useId();
  const triggerId = generatedId;
  const descriptionId = description ? `${triggerId}-description` : undefined;
  const errorId = error ? `${triggerId}-error` : undefined;
  const describedBy = [descriptionId, errorId].filter(Boolean).join(" ") || undefined;

  return (
    <div className={cn("flex flex-col gap-2", hideLabel && "gap-0")}>
      <label
        htmlFor={triggerId}
        className={cn(
          "text-label-md font-medium uppercase tracking-wide text-text-secondary",
          hideLabel && "sr-only",
        )}
      >
        {label}
        {required ? <span className="text-danger"> *</span> : null}
      </label>
      <SelectPrimitive.Root
        {...(value !== undefined && { value })}
        {...(defaultValue !== undefined && { defaultValue })}
        {...(onValueChange !== undefined && { onValueChange })}
        {...(disabled !== undefined && { disabled })}
        {...(required !== undefined && { required })}
        {...(name !== undefined && { name })}
      >
        <SelectPrimitive.Trigger
          id={triggerId}
          aria-invalid={Boolean(error) || undefined}
          aria-describedby={describedBy}
          className={cn(
            "flex h-11 w-full items-center justify-between rounded-sm border bg-surface-primary px-4 font-mono text-body-sm text-text-primary transition-colors duration-(--duration-fast) ease-standard data-[placeholder]:text-text-disabled disabled:cursor-not-allowed disabled:opacity-40",
            error
              ? "border-danger"
              : "border-border-default hover:border-border-hover data-[state=open]:border-border-focus",
            className,
          )}
        >
          <SelectPrimitive.Value placeholder={placeholder} />
          <SelectPrimitive.Icon asChild>
            <ChevronDown className="size-4 shrink-0 text-text-muted" aria-hidden="true" />
          </SelectPrimitive.Icon>
        </SelectPrimitive.Trigger>
        <SelectPrimitive.Portal>
          <SelectPrimitive.Content
            position="popper"
            sideOffset={4}
            className="z-(--z-dropdown) overflow-hidden rounded-sm border border-border-default bg-surface-elevated shadow-md"
          >
            <SelectPrimitive.Viewport className="p-1">
              {options.map((option) => (
                <SelectPrimitive.Item
                  key={option.value}
                  value={option.value}
                  disabled={option.disabled ?? false}
                  className="relative flex cursor-pointer select-none items-center rounded-xs py-2 pl-8 pr-3 font-mono text-body-sm text-text-primary outline-none data-[disabled]:pointer-events-none data-[disabled]:opacity-40 data-[highlighted]:bg-surface-hover"
                >
                  <span className="absolute left-2 flex size-4 items-center justify-center">
                    <SelectPrimitive.ItemIndicator>
                      <Check className="size-4 text-constructor-primary" aria-hidden="true" />
                    </SelectPrimitive.ItemIndicator>
                  </span>
                  <SelectPrimitive.ItemText>{option.label}</SelectPrimitive.ItemText>
                </SelectPrimitive.Item>
              ))}
            </SelectPrimitive.Viewport>
          </SelectPrimitive.Content>
        </SelectPrimitive.Portal>
      </SelectPrimitive.Root>
      {description ? (
        <p id={descriptionId} className="text-caption text-text-muted">
          {description}
        </p>
      ) : null}
      {error ? (
        <p id={errorId} role="alert" className="flex items-center gap-1 text-caption text-danger">
          <CircleAlert className="size-3.5 shrink-0" aria-hidden="true" />
          {error}
        </p>
      ) : null}
    </div>
  );
}
