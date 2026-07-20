import { Button } from "@pit-wall-insight/ui";
import { CircleAlert } from "lucide-react";
import { Component } from "react";
import type { ErrorInfo, ReactNode } from "react";

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
}

/**
 * Top-level render-error boundary. Before this, a single thrown render
 * error anywhere in the tree crashed the whole app to a blank white
 * screen with no recovery path (Phase 7 audit, Critical). Logs through
 * the same `reportClientError` sink used by the query client's global
 * error handlers, then offers a reload rather than leaving a blank page.
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  override state: ErrorBoundaryState = { hasError: false };

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  override componentDidCatch(error: unknown, errorInfo: ErrorInfo) {
    reportClientError(error, { componentStack: errorInfo.componentStack });
  }

  override render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen flex-col items-center justify-center gap-4 p-8 text-center">
          <CircleAlert className="size-10 text-danger" aria-hidden="true" />
          <h1 className="text-heading-md text-text-primary">Something went wrong</h1>
          <p className="max-w-md text-body-sm text-text-secondary">
            The application hit an unexpected error and couldn&apos;t continue. Reloading the page
            usually resolves this.
          </p>
          <Button onClick={() => window.location.reload()}>Reload</Button>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * The minimal client-side error sink the audit asked for: "even a
 * console.error today, a real reporting sink later." Centralized here so
 * the ErrorBoundary and the QueryClient's global onError handlers all
 * funnel through one place.
 */
export function reportClientError(error: unknown, context?: Record<string, unknown>) {
  console.error("[pit-wall-insight] client error", error, context);
}
