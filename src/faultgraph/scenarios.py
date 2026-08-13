"""Deterministic synthetic incidents with explicit ground truth."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta

from faultgraph.models import (
    CausalEdge,
    Evidence,
    EvidenceDirection,
    HypothesisSpec,
    Incident,
    NodeKind,
    ServiceNode,
    TelemetryPoint,
)

BASE_TIME = datetime(2026, 8, 13, 13, 4, tzinfo=UTC)


def _checksum(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _evidence(
    evidence_id: str,
    minute: int,
    source: str,
    direction: EvidenceDirection,
    statement: str,
    value: str,
) -> Evidence:
    payload = f"{evidence_id}|{minute}|{source}|{direction}|{statement}|{value}"
    return Evidence(
        id=evidence_id,
        timestamp=BASE_TIME + timedelta(minutes=minute),
        source=source,
        direction=direction,
        statement=statement,
        value=value,
        checksum=_checksum(payload),
    )


def _nodes(observed: Mapping[str, float]) -> list[ServiceNode]:
    specs = [
        ("edge", "edge-gateway", NodeKind.SERVICE, "platform", 24.0, 54, 34),
        ("orders", "order-router", NodeKind.SERVICE, "execution", 38.0, 238, 34),
        ("stream", "quote-stream", NodeKind.STREAM, "platform", 12.0, 238, 148),
        ("market", "market-data", NodeKind.SERVICE, "market-data", 18.0, 422, 148),
        ("risk", "risk-engine", NodeKind.SERVICE, "risk", 31.0, 606, 88),
        ("ledger", "ledger-writer", NodeKind.SERVICE, "accounting", 29.0, 790, 88),
        ("db", "orders-postgres", NodeKind.DATABASE, "data", 16.0, 974, 88),
    ]
    return [
        ServiceNode(
            id=node_id,
            name=name,
            kind=kind,
            owner=owner,
            baseline_latency_ms=baseline,
            observed_latency_ms=baseline + observed.get(node_id, 0.0),
            error_rate=min(0.36, observed.get(node_id, 0.0) / 900),
            x=x,
            y=y,
        )
        for node_id, name, kind, owner, baseline, x, y in specs
    ]


EDGES = [
    CausalEdge(source="edge", target="orders", coefficient=0.92, lag_ms=80, protocol="HTTP"),
    CausalEdge(
        source="orders", target="edge", coefficient=0.42, lag_ms=120, protocol="backpressure"
    ),
    CausalEdge(source="market", target="risk", coefficient=0.78, lag_ms=140, protocol="gRPC"),
    CausalEdge(source="stream", target="market", coefficient=0.88, lag_ms=220, protocol="Kafka"),
    CausalEdge(source="orders", target="risk", coefficient=0.71, lag_ms=110, protocol="gRPC"),
    CausalEdge(source="risk", target="ledger", coefficient=0.64, lag_ms=90, protocol="gRPC"),
    CausalEdge(source="ledger", target="db", coefficient=0.83, lag_ms=70, protocol="PostgreSQL"),
    CausalEdge(source="db", target="ledger", coefficient=0.72, lag_ms=160, protocol="lock wait"),
]


def _telemetry(observed: Mapping[str, float], onset: Mapping[str, int]) -> list[TelemetryPoint]:
    points: list[TelemetryPoint] = []
    baselines = {node.id: node.baseline_latency_ms for node in _nodes({})}
    for minute in range(0, 13):
        for node_id, baseline in baselines.items():
            start = onset.get(node_id, 99)
            progress = max(0.0, min(1.0, (minute - start + 1) / 3))
            deterministic_jitter = ((minute * 7 + len(node_id) * 3) % 5 - 2) * 0.35
            value = baseline + observed.get(node_id, 0.0) * progress + deterministic_jitter
            points.append(
                TelemetryPoint(
                    timestamp=BASE_TIME + timedelta(minutes=minute),
                    node_id=node_id,
                    metric="request.duration.p95",
                    value=round(max(0.1, value), 2),
                    baseline=baseline,
                    unit="ms",
                )
            )
    return points


def quote_stream_incident() -> Incident:
    observed = {"stream": 246, "market": 194, "risk": 152, "ledger": 85, "db": 63, "orders": 44}
    onset = {"stream": 2, "market": 3, "risk": 5, "orders": 6, "ledger": 7, "db": 8}
    evidence = [
        _evidence(
            "ev-1",
            2,
            "otel/quote-stream",
            EvidenceDirection.SUPPORTS,
            "Consumer lag began before downstream latency",
            "lag 42 → 18,430",
        ),
        _evidence(
            "ev-2",
            3,
            "deployments",
            EvidenceDirection.SUPPORTS,
            "No service deployment preceded the incident",
            "last deploy −9h",
        ),
        _evidence(
            "ev-3",
            5,
            "otel/market-data",
            EvidenceDirection.SUPPORTS,
            "Stale quote age tracks stream lag",
            "r=0.91",
        ),
        _evidence(
            "ev-4",
            6,
            "otel/orders-postgres",
            EvidenceDirection.CONTRADICTS,
            "Database saturation begins after risk latency",
            "+3m 12s",
        ),
        _evidence(
            "ev-5",
            8,
            "replay/seed-17",
            EvidenceDirection.SUPPORTS,
            "Removing broker throttle restores downstream latency",
            "82% reduction",
        ),
        _evidence(
            "ev-6",
            4,
            "otel/order-router",
            EvidenceDirection.CONTRADICTS,
            "Order volume remains inside baseline envelope",
            "p66",
        ),
    ]
    return Incident(
        id="INC-2026-0813-17",
        title="Stale quote decisions after stream throttling",
        summary=(
            "Risk decisions use delayed market data while database latency rises as a "
            "downstream symptom."
        ),
        started_at=BASE_TIME + timedelta(minutes=2),
        detected_at=BASE_TIME + timedelta(minutes=5),
        status="investigating",
        severity="SEV-1",
        environment="exchange-lab/us-east",
        ground_truth_node_id="stream",
        nodes=_nodes(observed),
        edges=EDGES,
        telemetry=_telemetry(observed, onset),
        evidence=evidence,
        hypotheses=[
            HypothesisSpec(
                id="h-stream",
                node_id="stream",
                title="Quote-stream replica throttling",
                mechanism=(
                    "Broker throttle increases consumer lag, aging quotes before risk evaluation."
                ),
                evidence_ids=["ev-1", "ev-2", "ev-3", "ev-5"],
                prior=0.34,
            ),
            HypothesisSpec(
                id="h-db",
                node_id="db",
                title="Orders database contention",
                mechanism=(
                    "Lock contention increases ledger latency and backs pressure into "
                    "risk evaluation."
                ),
                evidence_ids=["ev-4"],
                prior=0.31,
            ),
            HypothesisSpec(
                id="h-orders",
                node_id="orders",
                title="Order-router overload",
                mechanism=(
                    "A demand spike saturates routing workers and increases the full critical path."
                ),
                evidence_ids=["ev-6"],
                prior=0.35,
            ),
        ],
    )


def database_incident() -> Incident:
    observed = {"db": 270, "ledger": 215, "risk": 126, "orders": 91, "edge": 50}
    onset = {"db": 1, "ledger": 3, "risk": 5, "orders": 6, "edge": 7}
    evidence = [
        _evidence(
            "db-1",
            1,
            "postgres/locks",
            EvidenceDirection.SUPPORTS,
            "Lock wait time leads service latency",
            "p95 612ms",
        ),
        _evidence(
            "db-2",
            2,
            "otel/quote-stream",
            EvidenceDirection.CONTRADICTS,
            "Stream lag remains within baseline",
            "lag 31",
        ),
        _evidence(
            "db-3",
            5,
            "replay/seed-23",
            EvidenceDirection.SUPPORTS,
            "Terminating the blocking transaction restores the path",
            "76% reduction",
        ),
    ]
    return Incident(
        id="INC-2026-0809-04",
        title="Ledger backlog from lock convoy",
        summary=(
            "A long-running reconciliation transaction creates a lock convoy in the orders ledger."
        ),
        started_at=BASE_TIME - timedelta(days=4, minutes=9),
        detected_at=BASE_TIME - timedelta(days=4, minutes=4),
        status="resolved",
        severity="SEV-2",
        environment="exchange-lab/us-east",
        ground_truth_node_id="db",
        nodes=_nodes(observed),
        edges=EDGES,
        telemetry=_telemetry(observed, onset),
        evidence=evidence,
        hypotheses=[
            HypothesisSpec(
                id="h2-db",
                node_id="db",
                title="PostgreSQL lock convoy",
                mechanism="A blocking writer serializes ledger commits.",
                evidence_ids=["db-1", "db-3"],
                prior=0.45,
            ),
            HypothesisSpec(
                id="h2-stream",
                node_id="stream",
                title="Quote-stream consumer lag",
                mechanism="Delayed quotes prolong risk evaluation.",
                evidence_ids=["db-2"],
                prior=0.27,
            ),
            HypothesisSpec(
                id="h2-risk",
                node_id="risk",
                title="Risk worker saturation",
                mechanism="Worker saturation backs up order evaluation.",
                evidence_ids=[],
                prior=0.28,
            ),
        ],
    )


def order_router_incident() -> Incident:
    observed = {"orders": 220, "risk": 139, "ledger": 88, "db": 50, "edge": 74}
    onset = {"orders": 2, "edge": 3, "risk": 4, "ledger": 6, "db": 7}
    evidence = [
        _evidence(
            "or-1",
            2,
            "runtime/order-router",
            EvidenceDirection.SUPPORTS,
            "Runnable worker queue jumps before downstream latency",
            "3 → 96",
        ),
        _evidence(
            "or-2",
            2,
            "deployments",
            EvidenceDirection.SUPPORTS,
            "Concurrency limit changed before incident",
            "64 → 12",
        ),
        _evidence(
            "or-3",
            3,
            "postgres/locks",
            EvidenceDirection.CONTRADICTS,
            "No blocking transaction is present",
            "0 blockers",
        ),
    ]
    return Incident(
        id="INC-2026-0802-09",
        title="Router concurrency regression",
        summary="A configuration rollout reduces order-router concurrency below arrival rate.",
        started_at=BASE_TIME - timedelta(days=11, minutes=2),
        detected_at=BASE_TIME - timedelta(days=11),
        status="resolved",
        severity="SEV-2",
        environment="exchange-lab/us-west",
        ground_truth_node_id="orders",
        nodes=_nodes(observed),
        edges=EDGES,
        telemetry=_telemetry(observed, onset),
        evidence=evidence,
        hypotheses=[
            HypothesisSpec(
                id="h3-orders",
                node_id="orders",
                title="Order-router concurrency cap",
                mechanism="A low worker cap creates a runnable queue.",
                evidence_ids=["or-1", "or-2"],
                prior=0.42,
            ),
            HypothesisSpec(
                id="h3-db",
                node_id="db",
                title="Database contention",
                mechanism="Database locks slow ledger commits.",
                evidence_ids=["or-3"],
                prior=0.31,
            ),
            HypothesisSpec(
                id="h3-risk",
                node_id="risk",
                title="Risk model slowdown",
                mechanism="Feature evaluation consumes worker capacity.",
                evidence_ids=[],
                prior=0.27,
            ),
        ],
    )


def bundled_incidents() -> list[Incident]:
    return [quote_stream_incident(), database_incident(), order_router_incident()]
