import { describe, expect, test } from "vitest";

import { formatUsage } from "./usage";

describe("formatUsage", () => {
  test("formats total token usage", () => {
    expect(formatUsage({ total_tokens: 42 })).toBe("42 tokens");
  });

  test("returns fallback when usage is empty", () => {
    expect(formatUsage({})).toBe("No usage recorded");
  });
});
