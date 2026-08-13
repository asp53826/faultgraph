import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { RankedHypothesis } from "../api/types";
import { HypothesisTable } from "./HypothesisTable";

const hypotheses: RankedHypothesis[] = [
  {
    id: "h-stream",
    node_id: "stream",
    title: "Quote-stream replica throttling",
    mechanism: "Consumer lag ages quotes.",
    probability: 0.812,
    confidence_band: "high",
    supporting_evidence: [],
    contradictory_evidence: [],
    counterfactual: [],
    expected_impact_reduction: 0.73,
    falsification_test: "Replay without the throttle.",
  },
  {
    id: "h-db",
    node_id: "db",
    title: "Orders database contention",
    mechanism: "Lock contention backs up the ledger.",
    probability: 0.188,
    confidence_band: "low",
    supporting_evidence: [],
    contradictory_evidence: [],
    counterfactual: [],
    expected_impact_reduction: 0.21,
    falsification_test: "Replay without the blocker.",
  },
];

describe("HypothesisTable", () => {
  it("exposes ranking evidence and changes the selected hypothesis", async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();

    render(
      <HypothesisTable
        hypotheses={hypotheses}
        selectedId="h-stream"
        onSelect={onSelect}
        onExperiment={vi.fn()}
      />,
    );

    expect(screen.getByText("81.2%")).toBeInTheDocument();
    expect(screen.getByText("−73% impact")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /orders database contention/i }));
    expect(onSelect).toHaveBeenCalledWith("h-db");
  });

  it("keeps experiment execution behind an explicit action", async () => {
    const user = userEvent.setup();
    const onExperiment = vi.fn();

    render(
      <HypothesisTable
        hypotheses={hypotheses}
        selectedId="h-stream"
        onSelect={vi.fn()}
        onExperiment={onExperiment}
      />,
    );

    expect(onExperiment).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: /test selected/i }));
    expect(onExperiment).toHaveBeenCalledOnce();
  });
});
