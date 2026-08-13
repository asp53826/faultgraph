import { Braces, Clock3, RadioTower } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/client";
import { useResource } from "../api/useResource";
import { CausalGraph } from "../components/CausalGraph";
import { EvidenceInspector } from "../components/EvidenceInspector";
import { ExperimentDialog } from "../components/ExperimentDialog";
import { ExperimentLedger } from "../components/ExperimentLedger";
import { HypothesisTable } from "../components/HypothesisTable";
import { PropagationTape } from "../components/PropagationTape";
import { ResourceState } from "../components/ResourceState";
import { StatusMark } from "../components/StatusMark";

export function InvestigationPage() {
  const { incidentId = "" } = useParams();
  const incident = useResource(() => api.incident(incidentId), `incident:${incidentId}`);
  const analysis = useResource(() => api.analysis(incidentId), `analysis:${incidentId}`);
  const experiments = useResource(() => api.experiments(incidentId), `experiments:${incidentId}`);
  const [selectedId, setSelectedId] = useState("");
  const [mode, setMode] = useState<"observed" | "counterfactual">("observed");
  const [dialogOpen, setDialogOpen] = useState(false);
  useEffect(() => {
    if (analysis.data) setSelectedId(analysis.data.top_hypothesis_id);
  }, [analysis.data]);
  const selected = useMemo(
    () => analysis.data?.ranked_hypotheses.find((item) => item.id === selectedId) ?? analysis.data?.ranked_hypotheses[0],
    [analysis.data, selectedId],
  );
  if (incident.loading || analysis.loading || experiments.loading) return <ResourceState loading />;
  if (!incident.data || !analysis.data || !experiments.data || !selected) return <ResourceState error={incident.error ?? analysis.error ?? experiments.error} onRetry={() => { incident.reload(); analysis.reload(); experiments.reload(); }} />;
  const incidentData = incident.data;
  const started = new Date(incidentData.started_at);
  return (
    <div className="investigation-view">
      <header className="incident-header">
        <div>
          <div className="incident-header__meta"><StatusMark tone={incidentData.severity === "SEV-1" ? "confirmed" : "fault"} label={incidentData.severity} /><span>{incidentData.id}</span><span>{incidentData.environment}</span></div>
          <h1>{incidentData.title}</h1>
          <p>{incidentData.summary}</p>
        </div>
        <dl>
          <div><dt><Clock3 size={13} /> Started</dt><dd>{started.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", timeZone: "UTC" })} UTC</dd></div>
          <div><dt><RadioTower size={13} /> State</dt><dd>{incidentData.status}</dd></div>
          <div><dt><Braces size={13} /> Model</dt><dd>{analysis.data.method}</dd></div>
        </dl>
      </header>
      <PropagationTape incident={incidentData} selectedNodeId={selected.node_id} />
      <div className="causal-workspace">
        <section className="causal-workspace__field" aria-labelledby="causal-field-title">
          <div className="panel-heading panel-heading--graph"><div><span className="section-kicker">Intervention model</span><h2 id="causal-field-title">Causal field</h2></div><div className="segmented" role="group" aria-label="Causal field mode"><button type="button" className={mode === "observed" ? "active" : ""} onClick={() => setMode("observed")}>Observed</button><button type="button" className={mode === "counterfactual" ? "active" : ""} onClick={() => setMode("counterfactual")}>do({selected.node_id}=0)</button></div></div>
          <CausalGraph incident={incidentData} hypothesis={selected} mode={mode} />
        </section>
        <EvidenceInspector hypothesis={selected} />
      </div>
      <HypothesisTable hypotheses={analysis.data.ranked_hypotheses} selectedId={selected.id} onSelect={setSelectedId} onExperiment={() => setDialogOpen(true)} />
      <ExperimentLedger experiments={experiments.data} />
      <footer className="calibration-strip"><strong>Interpretation boundary</strong><span>{analysis.data.calibration_note}</span></footer>
      <ExperimentDialog open={dialogOpen} onOpenChange={setDialogOpen} hypothesis={selected} onRun={async (intervention, seed) => { const result = await api.runExperiment(incidentData.id, selected.id, intervention, seed); experiments.reload(); return result; }} />
    </div>
  );
}
