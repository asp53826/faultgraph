export type NodeKind = "service" | "database" | "stream" | "external";
export type EvidenceDirection = "supports" | "contradicts" | "context";

export interface IncidentSummary {
  id: string;
  title: string;
  severity: string;
  status: string;
  started_at: string;
  top_hypothesis: string;
  confidence: number;
  affected_nodes: number;
}

export interface ServiceNode {
  id: string;
  name: string;
  kind: NodeKind;
  owner: string;
  baseline_latency_ms: number;
  observed_latency_ms: number;
  error_rate: number;
  x: number;
  y: number;
}

export interface CausalEdge {
  source: string;
  target: string;
  coefficient: number;
  lag_ms: number;
  protocol: string;
}

export interface TelemetryPoint {
  timestamp: string;
  node_id: string;
  metric: string;
  value: number;
  baseline: number;
  unit: string;
}

export interface Evidence {
  id: string;
  timestamp: string;
  source: string;
  direction: EvidenceDirection;
  statement: string;
  value: string;
  checksum: string;
}

export interface HypothesisSpec {
  id: string;
  node_id: string;
  title: string;
  mechanism: string;
  evidence_ids: string[];
  prior: number;
}

export interface Incident {
  id: string;
  title: string;
  summary: string;
  started_at: string;
  detected_at: string;
  status: string;
  severity: string;
  environment: string;
  ground_truth_node_id?: string;
  nodes: ServiceNode[];
  edges: CausalEdge[];
  telemetry: TelemetryPoint[];
  evidence: Evidence[];
  hypotheses: HypothesisSpec[];
}

export interface CounterfactualEffect {
  node_id: string;
  observed_delta_ms: number;
  counterfactual_delta_ms: number;
  reduction_ratio: number;
}

export interface RankedHypothesis {
  id: string;
  node_id: string;
  title: string;
  mechanism: string;
  probability: number;
  confidence_band: "high" | "moderate" | "low";
  supporting_evidence: Evidence[];
  contradictory_evidence: Evidence[];
  counterfactual: CounterfactualEffect[];
  expected_impact_reduction: number;
  falsification_test: string;
}

export interface Analysis {
  incident_id: string;
  generated_at: string;
  method: string;
  assumptions: string[];
  ranked_hypotheses: RankedHypothesis[];
  top_hypothesis_id: string;
  calibration_note: string;
}

export interface ExperimentRecord {
  id: string;
  incident_id: string;
  hypothesis_id: string;
  intervention: string;
  seed: number;
  state: "planned" | "completed" | "rejected";
  created_at: string;
  completed_at: string | null;
  predicted_reduction: number | null;
  observed_reduction: number | null;
  manifest_sha256: string;
  conclusion: string | null;
}

export interface BenchmarkCase {
  incident_id: string;
  expected: string;
  predicted: string;
  reciprocal_rank: number;
  top1_correct: boolean;
  confidence: number;
}

export interface BenchmarkReport {
  cases: BenchmarkCase[];
  top1_accuracy: number;
  mean_reciprocal_rank: number;
  expected_calibration_error: number;
  limitations: string[];
}
