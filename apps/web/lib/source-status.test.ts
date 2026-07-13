import { describe, expect, test } from "vitest";

import { getSourceStatusMeta } from "./source-status";

describe("getSourceStatusMeta", () => {
  test("returns stable labels for known source statuses", () => {
    expect(getSourceStatusMeta("pending")).toEqual({ label: "Pending", tone: "amber" });
    expect(getSourceStatusMeta("processing")).toEqual({ label: "Processing", tone: "teal" });
    expect(getSourceStatusMeta("indexed")).toEqual({ label: "Indexed", tone: "green" });
    expect(getSourceStatusMeta("failed")).toEqual({ label: "Failed", tone: "red" });
  });

  test("returns fallback label for unknown source status", () => {
    expect(getSourceStatusMeta("paused")).toEqual({ label: "Paused", tone: "neutral" });
  });
});
