import { CheckCircle2, FileWarning, Fingerprint, TestTube2 } from "lucide-react";
import type { RankedHypothesis } from "../api/types";
import { StatusMark } from "./StatusMark";

interface EvidenceInspectorProps {
  hypothesis: RankedHypothesis;
}

export function EvidenceInspector({ hypothesis }: EvidenceInspectorProps) {
  return (
    <aside className="evidence-inspector" aria-labelledby="evidence-title">
      <div className="evidence-inspector__heading">
        <span className="section-kicker">Selected explanation</span>
        <h2 id="evidence-title">{hypothesis.title}</h2>
        <p>{hypothesis.mechanism}</p>
      </div>

      <dl className="evidence-stats">
        <div><dt>Rank score</dt><dd>{(hypothesis.probability * 100).toFixed(1)}%</dd></div>
        <div><dt>Predicted reduction</dt><dd>{Math.round(hypothesis.expected_impact_reduction * 100)}%</dd></div>
      </dl>

      <section className="evidence-group" aria-labelledby="supports-title">
        <h3 id="supports-title"><CheckCircle2 size={14} /> Supporting witnesses</h3>
        {hypothesis.supporting_evidence.length ? hypothesis.supporting_evidence.map((item) => (
          <article className="evidence-item" key={item.id}>
            <StatusMark tone="trace" label={item.source} />
            <p>{item.statement}</p>
            <strong>{item.value}</strong>
            <span><Fingerprint size={11} /> {item.checksum.slice(0, 12)}</span>
          </article>
        )) : <p className="empty-note">No supporting witness is attached.</p>}
      </section>

      <section className="evidence-group" aria-labelledby="contradictions-title">
        <h3 id="contradictions-title"><FileWarning size={14} /> Contradictions</h3>
        {hypothesis.contradictory_evidence.length ? hypothesis.contradictory_evidence.map((item) => (
          <article className="evidence-item evidence-item--contradiction" key={item.id}>
            <StatusMark tone="contradiction" label={item.source} />
            <p>{item.statement}</p>
            <strong>{item.value}</strong>
          </article>
        )) : <p className="empty-note">No contradictory witness is attached. Absence is not confirmation.</p>}
      </section>

      <section className="falsification-box">
        <h3><TestTube2 size={14} /> Falsification rule</h3>
        <p>{hypothesis.falsification_test}</p>
      </section>
    </aside>
  );
}
