import { getSourceStatusMeta } from "@/lib/source-status";
import type { KnowledgeSource } from "@/lib/types";

export function SourceStatusList({ sources }: { sources: KnowledgeSource[] }) {
  if (sources.length === 0) {
    return <div className="empty">No sources indexed yet.</div>;
  }

  return (
    <div className="list">
      {sources.map((source) => {
        const status = getSourceStatusMeta(source.status);

        return (
          <article className="row" key={source.id}>
            <div>
              <div className="row-title">{source.title}</div>
              <div className="row-meta">
                {source.source_type} · {source.uri || source.storage_path || "local content"}
              </div>
              {source.error_message ? <div className="row-meta">{source.error_message}</div> : null}
            </div>
            <span className="pill" data-tone={status.tone}>
              {status.label}
            </span>
          </article>
        );
      })}
    </div>
  );
}
