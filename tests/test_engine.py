from datetime import UTC

import pytest

from faultgraph.engine import analyze, benchmark
from faultgraph.scenarios import bundled_incidents, quote_stream_incident


def test_bundled_benchmark_recovers_each_injected_source() -> None:
    report = benchmark(bundled_incidents())

    assert len(report.cases) == 3
    assert report.top1_accuracy == 1.0
    assert report.mean_reciprocal_rank == 1.0
    assert all(case.predicted == case.expected for case in report.cases)
    assert 0 <= report.expected_calibration_error <= 1


def test_analysis_is_normalized_and_exposes_assumptions() -> None:
    incident = quote_stream_incident()
    analysis = analyze(incident, now=incident.detected_at.astimezone(UTC))

    assert analysis.top_hypothesis_id == "h-stream"
    assert sum(item.probability for item in analysis.ranked_hypotheses) == pytest.approx(
        1.0, abs=0.001
    )
    assert len(analysis.assumptions) >= 4
    assert "synthetic suite" in analysis.calibration_note


def test_counterfactual_intervention_removes_source_and_propagated_impact() -> None:
    analysis = analyze(quote_stream_incident())
    top = analysis.ranked_hypotheses[0]
    source = next(effect for effect in top.counterfactual if effect.node_id == top.node_id)
    downstream = next(effect for effect in top.counterfactual if effect.node_id == "market")

    assert source.counterfactual_delta_ms == 0
    assert source.reduction_ratio == 1
    assert downstream.counterfactual_delta_ms < downstream.observed_delta_ms
    assert downstream.reduction_ratio > 0.5
    assert top.expected_impact_reduction > 0.5


def test_contradictory_late_hypotheses_rank_below_supported_early_source() -> None:
    analysis = analyze(quote_stream_incident())
    positions = {item.node_id: index for index, item in enumerate(analysis.ranked_hypotheses)}

    assert positions["stream"] < positions["db"]
    assert positions["stream"] < positions["orders"]
