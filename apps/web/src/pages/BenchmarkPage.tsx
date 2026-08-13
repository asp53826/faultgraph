import { AlertCircle, CheckCircle2, Gauge } from "lucide-react";
import { api } from "../api/client";
import { useResource } from "../api/useResource";
import { ResourceState } from "../components/ResourceState";

export function BenchmarkPage() {
  const report = useResource(api.benchmark, "benchmark");
  if (report.loading) return <ResourceState loading />;
  if (!report.data) return <ResourceState error={report.error} onRetry={report.reload} />;
  return (
    <div className="research-page">
      <header className="research-page__header"><span className="section-kicker">Regression protocol · synthetic-exchange-v1</span><h1>Benchmark report</h1><p>This report checks whether model changes preserve diagnosis on the bundled labeled suite. It is deliberately too small to support a production-accuracy claim.</p></header>
      <section className="benchmark-ledger" aria-label="Aggregate benchmark measurements"><div className="benchmark-primary"><Gauge size={22} /><span>Top-1 accuracy</span><strong>{(report.data.top1_accuracy * 100).toFixed(0)}%</strong><small>{report.data.cases.length} deterministic cases</small></div><dl><div><dt>Mean reciprocal rank</dt><dd>{report.data.mean_reciprocal_rank.toFixed(3)}</dd></div><div><dt>Calibration error</dt><dd>{report.data.expected_calibration_error.toFixed(3)}</dd></div></dl></section>
      <section className="case-table"><div className="panel-heading"><div><span className="section-kicker">Ground-truth comparison</span><h2>Case ledger</h2></div></div><table><thead><tr><th>Incident</th><th>Expected source</th><th>Predicted source</th><th>Confidence</th><th>Result</th></tr></thead><tbody>{report.data.cases.map((item) => <tr key={item.incident_id}><td>{item.incident_id}</td><td>{item.expected}</td><td>{item.predicted}</td><td>{(item.confidence * 100).toFixed(1)}%</td><td>{item.top1_correct ? <span className="case-result case-result--pass"><CheckCircle2 size={13} /> pass</span> : <span className="case-result case-result--fail"><AlertCircle size={13} /> miss</span>}</td></tr>)}</tbody></table></section>
      <section className="limitations"><span className="section-kicker">Claim boundary</span><h2>Limitations retained with the result</h2><ul>{report.data.limitations.map((item) => <li key={item}>{item}</li>)}</ul></section>
    </div>
  );
}
