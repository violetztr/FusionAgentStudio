export type KnowledgeBase = {
  id: string;
  workspace_id: string;
  name: string;
  description: string;
};

export type Agent = {
  id: string;
  workspace_id: string;
  name: string;
  description: string;
  system_prompt: string;
  model_provider: string;
  model_name: string;
  temperature: number;
  top_k: number;
  citation_required: boolean;
  is_published: boolean;
  public_id: string;
};

export type ChatResponse = {
  conversation_id: string;
  answer: string;
  citations: Array<Record<string, unknown>>;
  usage: Record<string, unknown>;
};
