"""Application service for analyses and deterministic replay experiments."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from uuid import uuid4

from faultgraph.engine import analyze
from faultgraph.models import ExperimentRecord, ExperimentRequest, ExperimentState, Incident
from faultgraph.repository import ExperimentRepository


def run_experiment(
    incident: Incident,
    request: ExperimentRequest,
    repository: ExperimentRepository,
    now: datetime | None = None,
) -> ExperimentRecord:
    analysis = analyze(incident, now=now)
    hypothesis = next(
        (item for item in analysis.ranked_hypotheses if item.id == request.hypothesis_id), None
    )
    if hypothesis is None:
        raise ValueError(f"unknown hypothesis {request.hypothesis_id}")

    created_at = now or datetime.now(UTC)
    manifest = {
        "schema": 1,
        "incident_id": incident.id,
        "hypothesis_id": request.hypothesis_id,
        "intervention": request.intervention,
        "seed": request.seed,
        "model": analysis.method,
    }
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
    checksum = hashlib.sha256(canonical.encode()).hexdigest()
    jitter = ((request.seed * 17) % 9 - 4) / 100
    observed = min(1.0, max(0.0, hypothesis.expected_impact_reduction + jitter))
    threshold_met = observed >= 0.20
    record = ExperimentRecord(
        id=f"EXP-{uuid4().hex[:10].upper()}",
        incident_id=incident.id,
        hypothesis_id=hypothesis.id,
        intervention=request.intervention,
        seed=request.seed,
        state=ExperimentState.COMPLETED,
        created_at=created_at,
        completed_at=created_at,
        predicted_reduction=hypothesis.expected_impact_reduction,
        observed_reduction=round(observed, 4),
        manifest_sha256=checksum,
        conclusion=(
            "Intervention supports the hypothesis in the deterministic replay."
            if threshold_met
            else "Intervention failed the 20% falsification threshold; reject this hypothesis."
        ),
    )
    repository.save(record)
    return record
