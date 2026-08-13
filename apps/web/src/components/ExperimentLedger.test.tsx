import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { ExperimentRecord } from "../api/types";
import { ExperimentLedger } from "./ExperimentLedger";

const experiment: ExperimentRecord = {
  id: "EXP-TEST",
  incident_id: "INC-TEST",
  hypothesis_id: "h-stream",
  intervention: "Remove throttle and replay.",
  seed: 17,
  state: "completed",
  created_at: "2026-08-13T14:00:00Z",
  completed_at: "2026-08-13T14:00:00Z",
  predicted_reduction: 0.73,
  observed_reduction: 0.76,
  manifest_sha256: "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
  conclusion: "Supported in replay.",
};

describe("ExperimentLedger", () => {
  it("renders a retained replay without hiding its seed or manifest", () => {
    render(<ExperimentLedger experiments={[experiment]} />);

    expect(screen.getByText("EXP-TEST")).toBeInTheDocument();
    expect(screen.getByText("76%")).toBeInTheDocument();
    expect(screen.getByText("17")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /copy checksum/i })).toHaveTextContent("abcdef1234");
  });

  it("explains the empty state", () => {
    render(<ExperimentLedger experiments={[]} />);
    expect(screen.getByText(/no intervention has run/i)).toBeInTheDocument();
  });
});
