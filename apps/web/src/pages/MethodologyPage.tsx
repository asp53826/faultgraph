import { ArrowRight, Braces, Network, Scale, TestTube2 } from "lucide-react";

const steps = [
  { icon: Network, title: "Reconstruct", copy: "Align per-service p95 latency, anomaly onset, and a supplied influence graph." },
  { icon: Braces, title: "Rank", copy: "Combine temporal lead, prior odds, supporting witnesses, contradictions, and reachable impact." },
  { icon: TestTube2, title: "Intervene", copy: "Estimate do(X=0) with strongest damped paths so cyclic backpressure is not double-counted." },
  { icon: Scale, title: "Falsify", copy: "Replay a seeded workload and reject candidates below a declared 20% reduction threshold." },
];

const equation = `score(h) = logit(prior)
         + 1.50 · temporal_lead
         + 0.82 · supporting_witnesses
         − 1.15 · contradictions
         + 1.35 · reachable_impact

P(h) = softmax(score / 1.15)`;

export function MethodologyPage() {
  return (
    <div className="research-page methodology">
      <header className="research-page__header"><span className="section-kicker">Method card · dynamic-linear-influence-v1</span><h1>A diagnosis must survive intervention.</h1><p>FaultGraph separates hypothesis generation from causal evidence. The current engine is transparent and deterministic; it does not pretend a small synthetic benchmark establishes production validity.</p></header>
      <section className="method-flow" aria-label="Analysis procedure">{steps.map((step, index) => { const Icon = step.icon; return <div className="method-step" key={step.title}><span><Icon size={18} /></span><small>M{index + 1}</small><h2>{step.title}</h2><p>{step.copy}</p>{index < steps.length - 1 ? <ArrowRight className="method-step__arrow" size={17} aria-hidden="true" /> : null}</div>; })}</section>
      <div className="method-columns"><section><span className="section-kicker">Score equation</span><h2>Auditable ranking</h2><pre><code>{equation}</code></pre><p>The normalized score is a ranking probability, not a production posterior.</p></section><section><span className="section-kicker">Structural assumptions</span><h2>What must be true</h2><ol><li>The supplied influence graph represents the replay environment.</li><li>Edge coefficients remain below one, so cyclic effects decay.</li><li>Excess latency is a usable common response variable.</li><li>Experiment manifests contain every seed and intervention input.</li></ol></section></div>
      <section className="research-boundary"><div><span className="section-kicker">Future research</span><h2>Where learning belongs</h2></div><p>Learn topology proposals, response coefficients, and experiment policies from data—but retain held-out fault families, abstention, calibration, and the deterministic engine as a baseline. An LLM may explain evidence; it may not manufacture it.</p></section>
    </div>
  );
}
