import { AlertTriangle, RotateCw } from "lucide-react";

interface ResourceStateProps {
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
}

export function ResourceState({ loading, error, onRetry }: ResourceStateProps) {
  if (loading) return <div className="resource-state" aria-live="polite"><span className="loading-scan" /><strong>Reconstructing causal evidence…</strong><small>Loading incident, telemetry, and model output.</small></div>;
  return <div className="resource-state resource-state--error" role="alert"><AlertTriangle size={22} /><strong>Evidence service is unavailable</strong><p>{error ?? "The incident could not be loaded."}</p>{onRetry ? <button className="button button--quiet" type="button" onClick={onRetry}><RotateCw size={14} /> Retry</button> : null}</div>;
}
