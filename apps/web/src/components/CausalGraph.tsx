import { memo, useMemo } from "react";
import {
  Background,
  Controls,
  Handle,
  MarkerType,
  Position,
  ReactFlow,
  type Edge,
  type Node,
  type NodeProps,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import type { Incident, RankedHypothesis, ServiceNode } from "../api/types";

interface CausalNodeData extends Record<string, unknown> {
  service: ServiceNode;
  root: boolean;
  reduction: number;
  mode: "observed" | "counterfactual";
}

const CausalNode = memo(function CausalNode({ data }: NodeProps<Node<CausalNodeData>>) {
  const { service, root, reduction, mode } = data;
  const excess = service.observed_latency_ms - service.baseline_latency_ms;
  const displayedExcess = mode === "counterfactual" ? excess * (1 - reduction) : excess;
  const affected = displayedExcess > service.baseline_latency_ms * 0.25;
  const state = root ? "root" : affected ? "affected" : "stable";
  return (
    <div className={`causal-node causal-node--${state}`} aria-label={`${service.name}, ${state}`}>
      <Handle type="target" position={Position.Left} className="causal-handle" />
      <span className="causal-node__pin" aria-hidden="true" />
      <span className="causal-node__kind">{service.kind}</span>
      <strong>{service.name}</strong>
      <span className="causal-node__metric">
        +{Math.max(0, displayedExcess).toFixed(0)} ms
        {mode === "counterfactual" && reduction > 0.01 ? (
          <em> −{Math.round(reduction * 100)}%</em>
        ) : null}
      </span>
      <Handle type="source" position={Position.Right} className="causal-handle" />
    </div>
  );
});

const nodeTypes = { causal: CausalNode };

interface CausalGraphProps {
  incident: Incident;
  hypothesis: RankedHypothesis;
  mode: "observed" | "counterfactual";
}

export function CausalGraph({ incident, hypothesis, mode }: CausalGraphProps) {
  const reductionByNode = useMemo(
    () => new Map(hypothesis.counterfactual.map((effect) => [effect.node_id, effect.reduction_ratio])),
    [hypothesis],
  );
  const nodes = useMemo<Node<CausalNodeData>[]>(
    () =>
      incident.nodes.map((service) => ({
        id: service.id,
        type: "causal",
        position: { x: service.x, y: service.y },
        draggable: false,
        focusable: true,
        ariaLabel: `${service.name} causal node`,
        data: {
          service,
          root: service.id === hypothesis.node_id,
          reduction: reductionByNode.get(service.id) ?? 0,
          mode,
        },
      })),
    [hypothesis.node_id, incident.nodes, mode, reductionByNode],
  );
  const edges = useMemo<Edge[]>(
    () =>
      incident.edges.map((edge) => {
        const active =
          edge.source === hypothesis.node_id ||
          (reductionByNode.get(edge.source) ?? 0) > 0.05 ||
          (reductionByNode.get(edge.target) ?? 0) > 0.05;
        return {
          id: `${edge.source}-${edge.target}-${edge.protocol}`,
          source: edge.source,
          target: edge.target,
          label: `${edge.protocol} · ${edge.lag_ms}ms`,
          type: "smoothstep",
          animated: false,
          markerEnd: { type: MarkerType.ArrowClosed, width: 12, height: 12 },
          className: active ? "causal-edge causal-edge--active" : "causal-edge",
          labelStyle: { fill: active ? "#b8cbc7" : "#687a77", fontSize: 9 },
          labelBgStyle: { fill: "#10191b", fillOpacity: 0.92 },
          labelBgPadding: [4, 2],
        };
      }),
    [hypothesis.node_id, incident.edges, reductionByNode],
  );

  return (
    <div className="causal-field" role="region" aria-label={`${mode} causal field`}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.13 }}
        minZoom={0.62}
        maxZoom={1.7}
        nodesConnectable={false}
        elementsSelectable
        proOptions={{ hideAttribution: true }}
      >
        <Background color="rgba(216,234,230,.07)" gap={24} size={1} />
        <Controls showInteractive={false} position="bottom-right" />
      </ReactFlow>
      <div className="causal-field__legend" aria-label="Graph legend">
        <span><i className="legend-pin legend-pin--root" /> tested cause</span>
        <span><i className="legend-pin legend-pin--affected" /> excess latency</span>
        <span><i className="legend-pin legend-pin--stable" /> stable</span>
      </div>
    </div>
  );
}
