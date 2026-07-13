import { z } from "zod";

export const agentFormSchema = z.object({
  name: z.string().min(1).max(120),
  description: z.string(),
  system_prompt: z.string().min(1),
  model_name: z.string().min(1),
  temperature: z.number().min(0).max(2),
  top_k: z.number().int().min(1).max(20),
  citation_required: z.boolean(),
});

export type AgentFormValues = z.infer<typeof agentFormSchema>;
