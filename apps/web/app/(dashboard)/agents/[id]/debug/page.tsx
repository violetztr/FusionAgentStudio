import { DebugChat } from "@/components/agents/debug-chat";
import { apiGet } from "@/lib/api";
import type { Agent } from "@/lib/types";

export default async function AgentDebugPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const agent = await loadAgent(id);

  return (
    <>
      <header className="page-header">
        <div>
          <span className="eyebrow">Debug Console</span>
          <h1 className="page-title">{agent?.name ?? "Agent Debug"}</h1>
          <p className="page-subtitle">Inspect answers, citations, retrieval count, and model usage while tuning the agent.</p>
        </div>
      </header>
      <DebugChat agentId={id} />
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
