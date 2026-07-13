export type KnowledgeBase = {
  id: string;
  workspace_id: string;
  name: string;
  description: string;
};

export type KnowledgeSource = {
  id: string;
  knowledge_base_id: string;
  source_type: "pdf" | "docx" | "txt" | "markdown" | "web" | "note" | string;
  title: string;
  uri: string;
  storage_path: string;
  status: "pending" | "processing" | "indexed" | "failed" | string;
  error_message: string;
  metadata: Record<string, unknown>;
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

export type PublicAgent = {
  public_id: string;
  name: string;
  description: string;
};
