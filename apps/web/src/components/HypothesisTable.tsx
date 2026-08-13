import { FlaskConical } from "lucide-react";
import type { RankedHypothesis } from "../api/types";

interface HypothesisTableProps {
  hypotheses: RankedHypothesis[];
  selectedId: string;
  onSelect: (id: string) => void;
  onExperiment: () => void;
}

export function HypothesisTable({
  hypotheses,
  selectedId,
  onSelect,
  onExperiment,
}: HypothesisTableProps) {
  return (
    <section className="hypothesis-panel" aria-labelledby="hypothesis-title">
      <div className="panel-heading">
        <div>
          <span className="section-kicker">Ranked explanations</span>
          <h2 id="hypothesis-title">Hypotheses</h2>
        </div>
        <button className="button button--quiet" type="button" onClick={onExperiment}>
          <FlaskConical size={15} /> Test selected
        </button>
      </div>
      <ol className="hypothesis-table">
        {hypotheses.map((hypothesis, index) => (
          <li key={hypothesis.id}>
            <button
              type="button"
              className={`hypothesis-row ${hypothesis.id === selectedId ? "is-selected" : ""}`}
              onClick={() => onSelect(hypothesis.id)}
              aria-current={hypothesis.id === selectedId ? "true" : undefined}
            >
              <span className="hypothesis-row__rank">H{index + 1}</span>
              <span className="hypothesis-row__copy">
                <strong>{hypothesis.title}</strong>
                <small>{hypothesis.node_id} · {hypothesis.confidence_band} confidence</small>
              </span>
              <span className="confidence-track" aria-label={`${Math.round(hypothesis.probability * 100)} percent confidence`}>
                <i style={{ width: `${hypothesis.probability * 100}%` }} />
              </span>
              <span className="hypothesis-row__probability">
                {(hypothesis.probability * 100).toFixed(1)}%
              </span>
              <span className="hypothesis-row__impact">
                −{Math.round(hypothesis.expected_impact_reduction * 100)}% impact
              </span>
            </button>
          </li>
        ))}
      </ol>
    </section>
  );
}
