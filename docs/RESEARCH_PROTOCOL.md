# Research protocol

## Question

Can an auditable, supplied-topology influence model recover a known injected source and propose a counterfactual intervention that removes downstream excess latency in deterministic distributed-system incidents?

## Dataset

`synthetic-exchange-v1` contains three hand-authored incident fixtures:

1. quote-stream replica throttling;
2. PostgreSQL lock convoy;
3. order-router concurrency regression.

Every fixture includes a UTC timeline, service baselines, observed latency, typed graph edges, evidence statements with checksums, candidate hypotheses, and an injected ground-truth source. No fixture is claimed to represent the frequency or complexity of real production incidents.

## Primary measurements

- Top-1 source accuracy.
- Mean reciprocal rank.
- Five-bin expected calibration error using the top-ranked score.
- Counterfactual source removal and downstream reduction invariants.

## Falsification

Each hypothesis ships with a concrete replay test. The current deterministic replay rejects the hypothesis when modeled downstream reduction is below 20%. A replay record preserves the seed, intervention text, expected reduction, observed reduction, conclusion, and canonical manifest checksum.

## Reproduction

```bash
uv sync --all-groups
uv run pytest tests/test_engine.py
uv run faultgraph benchmark
```

The command must run from a clean checkout with no database state required. A change to engine behavior should be reviewed with the full case ledger, not only the aggregate score.

## Valid claims

- The test suite is deterministic at the recorded revision.
- The engine recovers a specific number of known injected sources in the bundled fixtures.
- Replay manifests with the same inputs produce the same checksum and reduction.

## Invalid claims

- Production root-cause accuracy.
- Learned causal effects.
- Generalization beyond the supplied topology and incidents.
- Superiority to an observability vendor or published causal-discovery method without a registered comparative study.
