import type { KnowledgeBase } from "@/lib/types";

export function KnowledgeBindingSelector({ knowledgeBases }: { knowledgeBases: KnowledgeBase[] }) {
  return (
    <section className="panel">
      <h2 className="panel-title">Bound Knowledge</h2>
      {knowledgeBases.length === 0 ? (
        <div className="empty">No knowledge bases available.</div>
      ) : (
        <div className="checkbox-list">
          {knowledgeBases.map((knowledgeBase) => (
            <label className="checkbox-row" key={knowledgeBase.id}>
              <input name="knowledge_base_ids" type="checkbox" value={knowledgeBase.id} />
              {knowledgeBase.name}
            </label>
          ))}
        </div>
      )}
    </section>
  );
}
