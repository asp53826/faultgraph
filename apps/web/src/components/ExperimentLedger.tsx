import { Check, Copy } from "lucide-react";
import { useState } from "react";
import type { ExperimentRecord } from "../api/types";

interface ExperimentLedgerProps {
  experiments: ExperimentRecord[];
}

export function ExperimentLedger({ experiments }: ExperimentLedgerProps) {
  const [copied, setCopied] = useState<string | null>(null);
  async function copyChecksum(experiment: ExperimentRecord) {
    await navigator.clipboard.writeText(experiment.manifest_sha256);
    setCopied(experiment.id);
    window.setTimeout(() => setCopied(null), 1200);
  }
  return (
    <section className="experiment-ledger" aria-labelledby="experiment-ledger-title">
      <div className="panel-heading panel-heading--compact">
        <div><span className="section-kicker">Reproducible evidence</span><h2 id="experiment-ledger-title">Experiment ledger</h2></div>
        <span className="data-note">{experiments.length} retained</span>
      </div>
      {experiments.length === 0 ? (
        <p className="ledger-empty">No intervention has run for this incident. Select a hypothesis and test it.</p>
      ) : (
        <div className="ledger-table-wrap">
          <table>
            <thead><tr><th>Run</th><th>Hypothesis</th><th>Observed</th><th>Seed</th><th>Manifest</th></tr></thead>
            <tbody>{experiments.map((experiment) => (
              <tr key={experiment.id}>
                <td><strong>{experiment.id}</strong><small>{experiment.state}</small></td>
                <td>{experiment.hypothesis_id}</td>
                <td>{experiment.observed_reduction === null ? "—" : `${Math.round(experiment.observed_reduction * 100)}%`}</td>
                <td>{experiment.seed}</td>
                <td><button type="button" className="checksum-button" onClick={() => void copyChecksum(experiment)} aria-label={`Copy checksum for ${experiment.id}`}>
                  {experiment.manifest_sha256.slice(0, 10)} {copied === experiment.id ? <Check size={12} /> : <Copy size={12} />}
                </button></td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      )}
    </section>
  );
}
