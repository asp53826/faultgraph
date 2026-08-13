# Security policy

## Supported versions

Security fixes target the latest release and the `main` branch.

## Reporting a vulnerability

Please use GitHub private vulnerability reporting for this repository. Do not open a public issue containing exploit details, secrets, private telemetry, or personally identifiable information.

Include the affected revision, reproduction conditions, expected impact, and the smallest safe proof of concept. You should receive an acknowledgement within five business days.

## Deployment boundary

The bundled application is a research workbench, not a multi-tenant incident platform. It has no user identity layer and should not be exposed to untrusted networks without an authenticating reverse proxy, rate limiting, centralized secrets, and a production database. See [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md).
