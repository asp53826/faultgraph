"""Typed contracts shared by the API, causal engine, and benchmark."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class NodeKind(StrEnum):
    SERVICE = "service"
    DATABASE = "database"
    STREAM = "stream"
    EXTERNAL = "external"


class EvidenceDirection(StrEnum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    CONTEXT = "context"


class ExperimentState(StrEnum):
    PLANNED = "planned"
    COMPLETED = "completed"
    REJECTED = "rejected"


class ServiceNode(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    kind: NodeKind
    owner: str
    baseline_latency_ms: float = Field(gt=0)
    observed_latency_ms: float = Field(gt=0)
    error_rate: float = Field(ge=0, le=1)
    x: float
    y: float


class CausalEdge(BaseModel):
    model_config = ConfigDict(frozen=True)

    source: str
    target: str
    coefficient: float = Field(gt=0, le=1)
    lag_ms: int = Field(ge=0)
    protocol: str


class TelemetryPoint(BaseModel):
    model_config = ConfigDict(frozen=True)

    timestamp: datetime
    node_id: str
    metric: str
    value: float
    baseline: float
    unit: str


class Evidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    timestamp: datetime
    source: str
    direction: EvidenceDirection
    statement: str
    value: str
    checksum: str


class HypothesisSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    node_id: str
    title: str
    mechanism: str
    evidence_ids: list[str]
    prior: float = Field(gt=0, lt=1)


class Incident(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    title: str
    summary: str
    started_at: datetime
    detected_at: datetime
    status: str
    severity: str
    environment: str
    ground_truth_node_id: str | None = None
    nodes: list[ServiceNode]
    edges: list[CausalEdge]
    telemetry: list[TelemetryPoint]
    evidence: list[Evidence]
    hypotheses: list[HypothesisSpec]


class CounterfactualEffect(BaseModel):
    node_id: str
    observed_delta_ms: float
    counterfactual_delta_ms: float
    reduction_ratio: float = Field(ge=0, le=1)


class RankedHypothesis(BaseModel):
    id: str
    node_id: str
    title: str
    mechanism: str
    probability: float = Field(ge=0, le=1)
    confidence_band: str
    supporting_evidence: list[Evidence]
    contradictory_evidence: list[Evidence]
    counterfactual: list[CounterfactualEffect]
    expected_impact_reduction: float = Field(ge=0, le=1)
    falsification_test: str


class Analysis(BaseModel):
    incident_id: str
    generated_at: datetime
    method: str
    assumptions: list[str]
    ranked_hypotheses: list[RankedHypothesis]
    top_hypothesis_id: str
    calibration_note: str


class ExperimentRequest(BaseModel):
    hypothesis_id: str
    intervention: str = Field(min_length=8, max_length=240)
    seed: int = Field(default=17, ge=0, le=2**31 - 1)


class ExperimentRecord(BaseModel):
    id: str
    incident_id: str
    hypothesis_id: str
    intervention: str
    seed: int
    state: ExperimentState
    created_at: datetime
    completed_at: datetime | None = None
    predicted_reduction: float | None = Field(default=None, ge=0, le=1)
    observed_reduction: float | None = Field(default=None, ge=0, le=1)
    manifest_sha256: str
    conclusion: str | None = None


class IncidentSummary(BaseModel):
    id: str
    title: str
    severity: str
    status: str
    started_at: datetime
    top_hypothesis: str
    confidence: float
    affected_nodes: int


class BenchmarkCaseResult(BaseModel):
    incident_id: str
    expected: str
    predicted: str
    reciprocal_rank: float
    top1_correct: bool
    confidence: float


class BenchmarkReport(BaseModel):
    cases: list[BenchmarkCaseResult]
    top1_accuracy: float
    mean_reciprocal_rank: float
    expected_calibration_error: float
    limitations: list[str]
