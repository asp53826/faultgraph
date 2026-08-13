import * as Dialog from "@radix-ui/react-dialog";
import { FlaskConical, X } from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";
import type { ExperimentRecord, RankedHypothesis } from "../api/types";

interface ExperimentDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  hypothesis: RankedHypothesis;
  onRun: (intervention: string, seed: number) => Promise<ExperimentRecord>;
}

export function ExperimentDialog({ open, onOpenChange, hypothesis, onRun }: ExperimentDialogProps) {
  const [intervention, setIntervention] = useState(`Remove the injected fault at ${hypothesis.node_id} and replay the captured workload.`);
  const [seed, setSeed] = useState(17);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setIntervention(`Remove the injected fault at ${hypothesis.node_id} and replay the captured workload.`);
    setError(null);
  }, [hypothesis]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setRunning(true);
    setError(null);
    try {
      await onRun(intervention, seed);
      onOpenChange(false);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Experiment failed.");
    } finally {
      setRunning(false);
    }
  }

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-overlay" />
        <Dialog.Content className="dialog-content" aria-describedby="experiment-description">
          <div className="dialog-heading">
            <span className="dialog-icon"><FlaskConical size={17} /></span>
            <div>
              <Dialog.Title>Plan deterministic replay</Dialog.Title>
              <Dialog.Description id="experiment-description">
                The intervention runs against the bundled isolated model, never production.
              </Dialog.Description>
            </div>
            <Dialog.Close className="icon-button" aria-label="Close experiment dialog"><X size={17} /></Dialog.Close>
          </div>
          <form onSubmit={(event) => void submit(event)}>
            <label>
              Hypothesis
              <input value={hypothesis.title} readOnly />
            </label>
            <label>
              Intervention manifest
              <textarea value={intervention} onChange={(event) => setIntervention(event.target.value)} minLength={8} maxLength={240} required />
            </label>
            <label>
              Replay seed
              <input type="number" min={0} max={2147483647} value={seed} onChange={(event) => setSeed(Number(event.target.value))} required />
            </label>
            <div className="experiment-preview">
              <span>Predicted impact reduction</span>
              <strong>{Math.round(hypothesis.expected_impact_reduction * 100)}%</strong>
            </div>
            {error ? <p className="form-error" role="alert">{error}</p> : null}
            <div className="dialog-actions">
              <Dialog.Close className="button button--quiet" type="button">Cancel</Dialog.Close>
              <button className="button button--primary" type="submit" disabled={running}>
                {running ? "Replaying…" : "Run isolated replay"}
              </button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
