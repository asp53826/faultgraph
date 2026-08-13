# FaultGraph interface system

## Direction

FaultGraph is a forensic instrument bench for a staff platform engineer who has
just received an incident page and needs to decide what failed, what merely
correlated with the failure, and which intervention is safe to run next. The
interface is dense, calm, and evidentiary. It should feel closer to a logic
analyzer and a flight-data recorder than to a generic observability dashboard.

Domain vocabulary: spans, propagation, intervention, counterfactual, witness,
contradiction, causal edge, replay, blast radius, and calibration.

## Signature

The observed/counterfactual causal field is aligned with a propagation tape.
Selecting a hypothesis changes both: the observed path remains fixed while the
counterfactual lane shows which downstream effects disappear under `do(X=0)`.
This signature also appears in hypothesis confidence tracks, evidence lineage,
intervention deltas, and incident-list propagation marks.

## Rejected defaults

- KPI card grids: evidence is organized by causal question, not metric type.
- Neon cyberpunk terminals: status colors carry meaning and are scarce.
- Decorative animated networks: nodes move only when an intervention changes
  the modeled graph state.
- Chat-first AI UI: investigation controls and evidence lead; prose is a report.

## Tokens

- `--basin`: #091113 — page canvas, like dark instrument glass.
- `--plate`: #10191b — primary work surface.
- `--plate-raised`: #152123 — inspectors and overlays.
- `--rule`: rgba(216, 234, 230, 0.10) — quiet structural boundary.
- `--evidence`: #e3ece9 — primary reading color.
- `--notation`: #92a39f — supporting labels and metadata.
- `--trace`: #86c8bf — observed, healthy, and selected evidence.
- `--fault`: #e7a15a — anomalous or unresolved fault propagation.
- `--confirmed`: #d66c66 — confirmed causal source only.
- `--contradiction`: #a791d4 — evidence that weakens a hypothesis.

No gradients. Status colors must never be used decoratively.

## Type and density

- UI/body: Spline Sans Variable, 14px base, 1.46 line height.
- Data/utility: Recursive Variable, 11–13px, tabular and slashed-zero features.
- Type ratio: 1.2. Hierarchy relies on weight and color before size.
- Spacing base: 4px. Workbench panels use 12–16px padding.
- Minimum interactive target: 40px desktop, 44px coarse pointer.

## Depth and shape

Depth uses surface-color shifts and low-opacity borders only. Shadows are
reserved for the command overlay. Inputs are darker than their parent surface.
Radius scale: 3px data cells, 6px controls, 10px major work surfaces, 14px
overlays. Causal nodes are chamfered rather than pill-shaped.

## Core patterns

- Workbench rail: 248px wide; same canvas color; 12px dense rows.
- Evidence inspector: 320px wide; one elevation above the causal field.
- Propagation tape: 72px high; service lanes align to graph columns.
- Causal node: 132×56px; 6px chamfer; two-tier label; status pin at left.
- Hypothesis row: 44px minimum; confidence track is inline, not a badge.
- Buttons: 36px visual height with 40px hit area and explicit focus ring.
- Command overlay: 600px max width; 160ms opacity/translate entrance.

## Motion

Only `transform` and `opacity` animate. Graph mode transitions use 180ms
`cubic-bezier(.23,1,.32,1)`. Repeated navigation and table selection have no
motion. `prefers-reduced-motion` removes graph translation and stagger.
