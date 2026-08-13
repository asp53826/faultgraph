import { useMemo } from "react";
import type { Incident } from "../api/types";

interface PropagationTapeProps {
  incident: Incident;
  selectedNodeId: string;
}

export function PropagationTape({ incident, selectedNodeId }: PropagationTapeProps) {
  const points = useMemo(() => {
    const times = incident.telemetry.map((point) => new Date(point.timestamp).getTime());
    const start = Math.min(...times);
    const end = Math.max(...times);
    const span = Math.max(1, end - start);
    return incident.nodes.map((node) => {
      const nodePoints = incident.telemetry.filter((point) => point.node_id === node.id);
      const onset = nodePoints.find(
        (point) => point.value >= point.baseline + Math.max(5, point.baseline * 0.25),
      );
      return {
        ...node,
        position: onset ? (new Date(onset.timestamp).getTime() - start) / span : null,
      };
    });
  }, [incident]);

  return (
    <section className="propagation-tape" aria-labelledby="propagation-title">
      <div className="section-label">
        <span id="propagation-title">Propagation tape</span>
        <span>T+00:00 — T+12:00</span>
      </div>
      <div className="propagation-tape__track" role="img" aria-label="Anomaly onset by service">
        <div className="propagation-tape__axis" aria-hidden="true">
          {Array.from({ length: 7 }, (_, index) => (
            <i key={index} style={{ left: `${(index / 6) * 100}%` }} />
          ))}
        </div>
        {points.map((node, index) =>
          node.position === null ? null : (
            <span
              key={node.id}
              className={`propagation-event ${node.id === selectedNodeId ? "is-source" : ""}`}
              style={{ left: `${node.position * 100}%`, top: `${7 + (index % 3) * 16}px` }}
              title={`${node.name} anomaly onset`}
            >
              <i />
              {node.name}
            </span>
          ),
        )}
      </div>
    </section>
  );
}
