# Threat model

## Assets

- Incident telemetry and evidence.
- Experiment manifests and conclusions.
- Analysis integrity and availability.
- The operator’s trust in what is observed versus inferred.

## Current trust boundaries

The bundled fixtures are trusted repository input. API clients are untrusted. SQLite is local to one application instance. Replay execution is a deterministic model function and does not connect to production infrastructure.

## Controls implemented

- Pydantic request and response validation.
- Explicit request size limits on intervention text and seed bounds.
- No shell execution, external URL fetch, template evaluation, or user-provided SQL.
- Parameterized SQLite queries.
- Canonical SHA-256 replay manifests.
- CORS allowlist and no credentialed cross-origin requests.
- CSP, frame denial, MIME sniffing prevention, restrictive browser permissions, and API no-store headers.
- Container execution as an unprivileged user.
- Read-only Kubernetes root filesystem with a dedicated data volume.
- CI verification for Python, TypeScript, tests, and container assembly.

The CSP permits inline style attributes because React Flow calculates graph transforms and geometry at runtime. Scripts remain restricted to same-origin bundles.

## Known gaps

- No identity, authorization, rate limiting, audit actor, or tenant isolation.
- SQLite permits one application replica in the provided deployment.
- Manifest checksums detect changes but do not prove who produced a record.
- Synthetic data does not exercise private-data retention or deletion requirements.
- The service has no production telemetry connector or fault-injection executor.

## Production hardening gate

Before exposing FaultGraph beyond a trusted lab network, add an identity-aware proxy, least-privilege roles, request and event rate limits, signed append-only manifests, centralized secret management, encrypted backups, retention policies, an external relational database, and an explicit approval gate for any real intervention executor.
