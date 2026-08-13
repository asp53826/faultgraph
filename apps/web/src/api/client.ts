import type {
  Analysis,
  BenchmarkReport,
  ExperimentRecord,
  Incident,
  IncidentSummary,
} from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { Accept: "application/json", "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(payload?.detail ?? `Request failed with status ${response.status}`);
  }
  return (await response.json()) as T;
}

export const api = {
  incidents: () => request<IncidentSummary[]>("/api/incidents"),
  incident: (id: string) => request<Incident>(`/api/incidents/${encodeURIComponent(id)}`),
  analysis: (id: string) =>
    request<Analysis>(`/api/incidents/${encodeURIComponent(id)}/analysis`),
  experiments: (id: string) =>
    request<ExperimentRecord[]>(`/api/incidents/${encodeURIComponent(id)}/experiments`),
  runExperiment: (id: string, hypothesisId: string, intervention: string, seed: number) =>
    request<ExperimentRecord>(`/api/incidents/${encodeURIComponent(id)}/experiments`, {
      method: "POST",
      body: JSON.stringify({ hypothesis_id: hypothesisId, intervention, seed }),
    }),
  benchmark: () => request<BenchmarkReport>("/api/benchmark"),
};
