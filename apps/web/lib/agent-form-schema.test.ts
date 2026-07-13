import { describe, expect, test } from "vitest";

import { agentFormSchema } from "./agent-form-schema";

describe("agentFormSchema", () => {
  test("accepts a valid agent configuration", () => {
    const parsed = agentFormSchema.safeParse({
      name: "Support Agent",
      description: "Answers support questions",
      system_prompt: "Use bound knowledge only.",
      model_name: "gpt-4.1-mini",
      temperature: 0.2,
      top_k: 8,
      citation_required: true,
    });

    expect(parsed.success).toBe(true);
  });

  test("rejects invalid numeric settings", () => {
    const parsed = agentFormSchema.safeParse({
      name: "Support Agent",
      description: "",
      system_prompt: "Use bound knowledge only.",
      model_name: "gpt-4.1-mini",
      temperature: 3,
      top_k: 25,
      citation_required: true,
    });

    expect(parsed.success).toBe(false);
  });
});
