export interface RouteholderPageProps {
  title: string;
}

/**
 * Deliberately empty placeholder — proves routing/navigation work without
 * building any dashboard content (out of scope for the application shell).
 */
export function RouteholderPage({ title }: RouteholderPageProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-24 text-center">
      <p className="font-mono text-caption uppercase tracking-wide text-text-muted">Coming soon</p>
      <h1 className="font-display text-heading-lg text-text-primary">{title}</h1>
    </div>
  );
}
