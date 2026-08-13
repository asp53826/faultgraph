# Contributing

FaultGraph values falsifiable improvements over impressive-looking output.

## Development contract

1. Open an issue describing the failure mode, model change, or interface problem.
2. Add a deterministic regression case before changing ranking behavior.
3. Preserve each analysis assumption and benchmark limitation unless the underlying limitation is actually removed.
4. Run the complete verification suite from the README.
5. Keep generated artifacts, credentials, private telemetry, and large datasets out of Git.

Model changes must report the pre-change and post-change result for every bundled case. A higher benchmark score is insufficient if calibration error worsens or the explanation becomes less auditable.

Interface changes must preserve keyboard access, visible focus, reduced-motion behavior, graph text alternatives, and the compact forensic-instrument visual system in [.interface-design/system.md](.interface-design/system.md).
