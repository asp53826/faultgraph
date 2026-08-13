# Architecture decision record

## Context

Incident analysis needs to preserve three different kinds of evidence: what was observed, what the model infers, and what an intervention actually changed. Collapsing these into one “root cause” label makes a system easy to demo and hard to trust.

## Decision

FaultGraph separates the system into five bounded layers:

| Layer | Responsibility | Deliberate non-responsibility |
|---|---|---|
| Scenario contracts | Versioned topology, telemetry, evidence, hypotheses, ground truth | Live telemetry ingestion |
| Analysis engine | Onset extraction, influence propagation, ranking, counterfactual estimates | Unrestricted causal discovery |
| Application service | Seeded replay manifests and falsification conclusions | Production fault injection |
| API and repository | Typed HTTP contracts, SSE notifications, durable experiment records | Multi-tenant authorization |
| Workbench | Comparison, navigation, intervention planning, claim boundaries | Recomputing model results in the browser |

The browser never contains a second analysis implementation. It renders API contracts so model and interface evidence cannot silently diverge.

## Causal calculation

For candidate source `s`, the influence on node `v` is the strongest damped directed path:

```text
I(s, s) = 1
I(s, v) = max over paths(s → v) of product(edge coefficient)
```

The counterfactual excess latency is:

```text
delta_cf(v | do(s=0)) = max(0, delta_observed(v) - delta_observed(s) * I(s, v))
```

Max-product propagation was chosen over additive path aggregation because the supplied graph contains feedback cycles. Additive propagation could count the same symptom repeatedly and inflate confidence.

Candidate scores combine prior log odds, anomaly onset lead, supporting and contradictory evidence counts, and expected impact reduction. A temperature-scaled softmax with temperature `3.0` avoids presenting the small synthetic evidence base with false numerical certainty. The scores are comparable only within one incident, and the output labels them as normalized ranking scores.

## Persistence

Incidents are immutable bundled fixtures. Replay experiments are persisted in SQLite as complete versioned JSON records. Each replay manifest is canonicalized with sorted keys and compact separators, then addressed by SHA-256. A future production implementation should move incidents and experiments to an append-only relational store and sign manifests at an external trust boundary.

## Consequences

- Results are reproducible and the inference path is inspectable.
- Synthetic incidents can exercise the complete system without pretending to be private production telemetry.
- One SQLite replica is a deployment constraint, reflected in the Kubernetes manifest.
- Changing topology assumptions can change every counterfactual; the API therefore returns those assumptions with the result.
