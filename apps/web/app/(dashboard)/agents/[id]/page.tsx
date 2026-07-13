import { AgentForm } from "@/components/agents/agent-form";
import { KnowledgeBindingSelector } from "@/components/agents/knowledge-binding-selector";
import { ModelSettings } from "@/components/agents/model-settings";
import { PublishControls } from "@/components/agents/publish-controls";
import { apiGet } from "@/lib/api";
import type { Agent, KnowledgeBase } from "@/lib/types";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000001";

export default async function AgentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [agent, knowledgeBases] = await Promise.all([loadAgent(id), loadKnowledgeBases()]);

  return (
    <>
      <header className="page-header">
        <div>
          <span className="eyebrow">Agent Builder</span>
          <h1 className="page-title">{agent?.name ?? "Agent Configuration"}</h1>
          <p className="page-subtitle">{agent?.description || "Tune instructions, retrieval, citations, and release state."}</p>
        </div>
      </header>

      <div className="builder-grid">
        <div className="builder-column">
          <AgentForm agent={agent} />
          <KnowledgeBindingSelector knowledgeBases={knowledgeBases} />
        </div>
        <div className="builder-column">
          <ModelSettings agent={agent} />
          <PublishControls agent={agent} />
        </div>
      </div>
    </>
  );
}

async function loadAgent(id: string) {
  try {
    return await apiGet<Agent>(`/api/agents/${id}`);
  } catch {
    return null;
  }
}

async function loadKnowledgeBases() {
  try {
    return await apiGet<KnowledgeBase[]>(`/api/knowledge-bases?workspace_id=${WORKSPACE_ID}`);
  } catch {
    return [];
  }
}
