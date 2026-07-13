import { apiGet } from "@/lib/api";
import type { KnowledgeBase } from "@/lib/types";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000001";

export default async function KnowledgeBasesPage() {
  const knowledgeBases = await loadKnowledgeBases();

  return (
    <>
      <header className="page-header">
        <div>
          <span className="eyebrow">Knowledge Center</span>
          <h1 className="page-title">Knowledge Bases</h1>
          <p className="page-subtitle">
            Source collections that agents can retrieve from, cite, and combine during grounded answers.
          </p>
        </div>
        <button className="button" type="button">
          New Knowledge Base
        </button>
      </header>

      <section className="section">
        {knowledgeBases.length === 0 ? (
          <div className="empty">No knowledge bases yet.</div>
        ) : (
          <div className="list">
            {knowledgeBases.map((item) => (
              <article className="row" key={item.id}>
                <div>
                  <div className="row-title">{item.name}</div>
                  <div className="row-meta">{item.description || "No description"}</div>
                </div>
                <span className="pill">Ready</span>
              </article>
            ))}
          </div>
        )}
      </section>
    </>
  );
}

async function loadKnowledgeBases() {
  try {
    return await apiGet<KnowledgeBase[]>(`/api/knowledge-bases?workspace_id=${WORKSPACE_ID}`);
  } catch {
    return [];
  }
}
