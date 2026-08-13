"""Transparent causal ranking and intervention analysis.

This is a dynamic linear influence model, not unrestricted causal discovery.
Its assumptions are emitted with every result so the UI cannot present an
unqualified probability as ground truth.
"""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import UTC, datetime

from faultgraph.models import (
    Analysis,
    BenchmarkCaseResult,
    BenchmarkReport,
    CounterfactualEffect,
    EvidenceDirection,
    Incident,
    RankedHypothesis,
)


def _observed_deltas(incident: Incident) -> dict[str, float]:
    return {
        node.id: max(0.0, node.observed_latency_ms - node.baseline_latency_ms)
        for node in incident.nodes
    }


def _onsets(incident: Incident) -> dict[str, datetime]:
    onset: dict[str, datetime] = {}
    for point in sorted(incident.telemetry, key=lambda item: item.timestamp):
        threshold = point.baseline + max(5.0, point.baseline * 0.25)
        if point.value >= threshold and point.node_id not in onset:
            onset[point.node_id] = point.timestamp
    return onset


def _influence(incident: Incident, source: str) -> dict[str, float]:
    """Return the strongest damped path from source to each node.

    Using a max-product path prevents cycles from double-counting evidence.
    The update converges because every edge coefficient is strictly below one.
    """

    influence = {node.id: 0.0 for node in incident.nodes}
    influence[source] = 1.0
    adjacency: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for edge in incident.edges:
        adjacency[edge.source].append((edge.target, edge.coefficient))

    for _ in range(len(incident.nodes) * 2):
        changed = False
        for parent, children in adjacency.items():
            for child, coefficient in children:
                candidate = influence[parent] * coefficient
                if candidate > influence[child] + 1e-9:
                    influence[child] = candidate
                    changed = True
        if not changed:
            break
    return influence


def _counterfactual(incident: Incident, node_id: str) -> tuple[list[CounterfactualEffect], float]:
    deltas = _observed_deltas(incident)
    influence = _influence(incident, node_id)
    source_delta = deltas[node_id]
    effects: list[CounterfactualEffect] = []
    removed_total = 0.0
    observed_total = sum(deltas.values()) or 1.0
    for node in incident.nodes:
        observed = deltas[node.id]
        removed = min(observed, source_delta * influence[node.id])
        counterfactual = max(0.0, observed - removed)
        reduction = removed / observed if observed else 0.0
        removed_total += removed
        effects.append(
            CounterfactualEffect(
                node_id=node.id,
                observed_delta_ms=round(observed, 2),
                counterfactual_delta_ms=round(counterfactual, 2),
                reduction_ratio=round(reduction, 4),
            )
        )
    return effects, min(1.0, removed_total / observed_total)


def _softmax(scores: list[float], temperature: float = 3.0) -> list[float]:
    maximum = max(scores)
    values = [math.exp((score - maximum) / temperature) for score in scores]
    total = sum(values)
    return [value / total for value in values]


def analyze(incident: Incident, now: datetime | None = None) -> Analysis:
    evidence = {item.id: item for item in incident.evidence}
    onsets = _onsets(incident)
    if onsets:
        first = min(onsets.values())
        last = max(onsets.values())
        span = max(1.0, (last - first).total_seconds())
    else:
        first = incident.started_at
        span = 1.0

    provisional: list[tuple[float, float, list[CounterfactualEffect]]] = []
    for hypothesis in incident.hypotheses:
        related = [evidence[item] for item in hypothesis.evidence_ids if item in evidence]
        supports = sum(item.direction == EvidenceDirection.SUPPORTS for item in related)
        contradicts = sum(item.direction == EvidenceDirection.CONTRADICTS for item in related)
        onset = onsets.get(hypothesis.node_id)
        temporal_lead = 0.0 if onset is None else 1.0 - ((onset - first).total_seconds() / span)
        effects, impact = _counterfactual(incident, hypothesis.node_id)
        prior_log_odds = math.log(hypothesis.prior / (1 - hypothesis.prior))
        score = (
            prior_log_odds
            + 1.5 * temporal_lead
            + 0.82 * supports
            - 1.15 * contradicts
            + 1.35 * impact
        )
        provisional.append((score, impact, effects))

    probabilities = _softmax([item[0] for item in provisional])
    ranked: list[RankedHypothesis] = []
    for hypothesis, probability, (_, impact, effects) in zip(
        incident.hypotheses, probabilities, provisional, strict=True
    ):
        related = [evidence[item] for item in hypothesis.evidence_ids if item in evidence]
        ranked.append(
            RankedHypothesis(
                id=hypothesis.id,
                node_id=hypothesis.node_id,
                title=hypothesis.title,
                mechanism=hypothesis.mechanism,
                probability=round(probability, 4),
                confidence_band=(
                    "high" if probability >= 0.75 else "moderate" if probability >= 0.45 else "low"
                ),
                supporting_evidence=[
                    item for item in related if item.direction == EvidenceDirection.SUPPORTS
                ],
                contradictory_evidence=[
                    item for item in related if item.direction == EvidenceDirection.CONTRADICTS
                ],
                counterfactual=effects,
                expected_impact_reduction=round(impact, 4),
                falsification_test=(
                    f"Replay the captured workload with an isolated intervention on "
                    f"{hypothesis.node_id}; reject if downstream excess latency falls "
                    "by less than 20%."
                ),
            )
        )

    ranked.sort(key=lambda item: item.probability, reverse=True)
    generated_at = now or datetime.now(UTC)
    return Analysis(
        incident_id=incident.id,
        generated_at=generated_at,
        method="dynamic-linear-influence-v1",
        assumptions=[
            "The supplied service influence graph is structurally correct for this replay.",
            "Anomalies above 25% of baseline are comparable after conversion to excess latency.",
            "Edge coefficients are local response strengths, not learned causal effects "
            "from production.",
            "Counterfactual reduction uses the strongest damped path and does not "
            "double-count cycles.",
        ],
        ranked_hypotheses=ranked,
        top_hypothesis_id=ranked[0].id,
        calibration_note=(
            "Probabilities are normalized ranking scores calibrated only on the bundled "
            "synthetic suite; "
            "they must not be interpreted as production posterior probabilities."
        ),
    )


def _expected_calibration_error(results: list[BenchmarkCaseResult], bins: int = 5) -> float:
    error = 0.0
    for index in range(bins):
        lower = index / bins
        upper = (index + 1) / bins
        members = [
            item
            for item in results
            if lower <= item.confidence <= upper and (item.confidence < upper or index == bins - 1)
        ]
        if not members:
            continue
        accuracy = sum(item.top1_correct for item in members) / len(members)
        confidence = sum(item.confidence for item in members) / len(members)
        error += (len(members) / len(results)) * abs(accuracy - confidence)
    return error


def benchmark(incidents: list[Incident]) -> BenchmarkReport:
    results: list[BenchmarkCaseResult] = []
    for incident in incidents:
        if incident.ground_truth_node_id is None:
            continue
        analysis = analyze(incident, now=incident.detected_at)
        node_ranking = [item.node_id for item in analysis.ranked_hypotheses]
        rank = node_ranking.index(incident.ground_truth_node_id) + 1
        results.append(
            BenchmarkCaseResult(
                incident_id=incident.id,
                expected=incident.ground_truth_node_id,
                predicted=node_ranking[0],
                reciprocal_rank=round(1 / rank, 4),
                top1_correct=rank == 1,
                confidence=analysis.ranked_hypotheses[0].probability,
            )
        )
    count = len(results) or 1
    return BenchmarkReport(
        cases=results,
        top1_accuracy=round(sum(item.top1_correct for item in results) / count, 4),
        mean_reciprocal_rank=round(sum(item.reciprocal_rank for item in results) / count, 4),
        expected_calibration_error=round(_expected_calibration_error(results), 4),
        limitations=[
            "The bundled suite contains three deterministic synthetic incidents.",
            "Topology and coefficients are provided rather than discovered from raw "
            "production telemetry.",
            "Accuracy on this suite is a regression signal, not evidence of external validity.",
            "No comparison to commercial observability products is claimed.",
        ],
    )
