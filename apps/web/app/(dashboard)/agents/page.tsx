import { apiGet } from "@/lib/api";
import type { Agent } from "@/lib/types";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000001";

export default async function AgentsPage() {
  const agents = await loadAgents();

  return (
    <>
      <header className="page-header">
        <div>
          <span className="eyebrow">Agent Builder</span>
          <h1 className="page-title">Agents</h1>
          <p className="page-subtitle">
            Configured assistants with prompts, model settings, citation policy, and bound knowledge bases.
          </p>
        </div>
        <button className="button" type="button">
          New Agent
        </button>
      </header>

      <section className="section">
        {agents.length === 0 ? (
          <div className="empty">No agents yet.</div>
        ) : (
          <div className="list">
            {agents.map((agent) => (
              <article className="row" key={agent.id}>
                <div>
                  <div className="row-title">{agent.name}</div>
                  <div className="row-meta">
                    {agent.model_name} · top {agent.top_k} · citations {agent.citation_required ? "on" : "off"}
                  </div>
                </div>
                <span className="pill">{agent.is_published ? "Published" : "Draft"}</span>
              </article>
            ))}
          </div>
        )}
      </section>
    </>
  );
}

async function loadAgents() {
  try {
    return await apiGet<Agent[]>(`/api/agents?workspace_id=${WORKSPACE_ID}`);
  } catch {
    return [];
  }
}
