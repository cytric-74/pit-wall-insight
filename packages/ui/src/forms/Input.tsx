import { CircleAlert } from "lucide-react";
import { forwardRef, useId } from "react";
import type { InputHTMLAttributes } from "react";

import { cn } from "../lib/cn.js";

export interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "id"> {
  /** Always required (docs/assets/13_ACCESSIBILITY_VISUALS.md: "Every input
   * requires a Visible label" — placeholder text never replaces it). */
  label: string;
  description?: string;
  error?: string;
  id?: string;
}

/**
 * "Inputs should feel Precise, Technical, Clean... Focus is communicated by
 * accent, not animation." (docs/assets/09_COMPONENT_STYLING.md)
 */
export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, description, error, id, required, ...props }, ref) => {
    const generatedId = useId();
    const inputId = id ?? generatedId;
    const descriptionId = description ? `${inputId}-description` : undefined;
    const errorId = error ? `${inputId}-error` : undefined;
    const describedBy = [descriptionId, errorId].filter(Boolean).join(" ") || undefined;

    return (
      <div className="flex flex-col gap-2">
        <label
          htmlFor={inputId}
          className="text-label-md font-medium uppercase tracking-wide text-text-secondary"
        >
          {label}
          {required ? <span className="text-danger"> *</span> : null}
        </label>
        <input
          ref={ref}
          id={inputId}
          required={required}
          aria-invalid={Boolean(error) || undefined}
          aria-describedby={describedBy}
          className={cn(
            "h-11 rounded-sm border bg-surface-primary px-4 font-mono text-body-sm text-text-primary transition-colors duration-(--duration-fast) ease-standard placeholder:text-text-disabled disabled:cursor-not-allowed disabled:opacity-40",
            error
              ? "border-danger"
              : "border-border-default hover:border-border-hover focus:border-border-focus",
            className,
          )}
          {...props}
        />
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
  },
);
Input.displayName = "Input";
