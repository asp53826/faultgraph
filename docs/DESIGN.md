# Interface rationale

FaultGraph is designed as forensic instrumentation, not a generic analytics dashboard. Its signature view is the intersection of a fault-propagation tape and an observed-versus-counterfactual causal field. The interface avoids a card-grid homepage, neon “AI terminal” styling, decorative network animation, and unsupported autonomous-agent claims.

## Visual grammar

- Deep ink surfaces keep the graph legible without black-on-neon spectacle.
- Sea-glass green marks selected evidence and interventions.
- Amber is reserved for active faults; red is reserved for contradiction or destructive risk.
- Spline Sans handles operational reading; Recursive Mono is limited to identifiers, measurements, checksums, and source labels.
- Borders and one-step surface shifts carry hierarchy. Panels use compact spacing and square geometry.
- Motion is functional and short, with a complete `prefers-reduced-motion` fallback.

The reusable token and component rules live in [`.interface-design/system.md`](../.interface-design/system.md).

## 21st.dev review

Connected 21st.dev components were inspected as pattern references, not copied as a generated application:

- [Data Grid Table](https://21st.dev/@sean0205/data-grid-table): informed dense row scanning and separate row/action targets.
- [Command Palette](https://21st.dev/@ddoemonn/command-palette): informed keyboard-first navigation and grouped search results.
- [Incident Chart](https://21st.dev/@reaviz/incident-chart): informed the shared-time-axis propagation tape; its multicolor decorative treatment was rejected.
- [N8N Workflow Block](https://21st.dev/@moumensoliman/n8n-workflow-block-shadcnui): informed bounded graph navigation and node geometry; gradient/glass styling and animated drag were rejected.

That review changed interaction details while preserving a product-specific visual language.
