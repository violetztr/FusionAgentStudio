"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";

import { getSourceStatusMeta } from "@/lib/source-status";
import { reindexSource } from "@/lib/source-api";
import type { KnowledgeSource } from "@/lib/types";

export function SourceStatusList({ sources }: { sources: KnowledgeSource[] }) {
  const router = useRouter();
  const [activeSourceId, setActiveSourceId] = useState<string | null>(null);
  const [errorSourceId, setErrorSourceId] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  if (sources.length === 0) {
    return <div className="empty">No sources indexed yet.</div>;
  }

  function reindex(sourceId: string) {
    setActiveSourceId(sourceId);
    setErrorSourceId(null);
    startTransition(async () => {
      try {
        await reindexSource(sourceId);
        router.refresh();
      } catch {
        setErrorSourceId(sourceId);
      } finally {
        setActiveSourceId(null);
      }
    });
  }

  return (
    <div className="list">
      {sources.map((source) => {
        const status = getSourceStatusMeta(source.status);
        const isActive = isPending && activeSourceId === source.id;

        return (
          <article className="row" key={source.id}>
            <div>
              <div className="row-title">{source.title}</div>
              <div className="row-meta">
                {source.source_type} · {source.uri || source.storage_path || "local content"}
              </div>
              {source.error_message ? <div className="row-meta">{source.error_message}</div> : null}
              {errorSourceId === source.id ? <div className="row-meta">Reindex failed.</div> : null}
            </div>
            <div className="status-line">
              <span className="pill" data-tone={status.tone}>
                {status.label}
              </span>
              <button className="button" disabled={isActive} onClick={() => reindex(source.id)} type="button">
                {isActive ? "Indexing" : "Reindex"}
              </button>
            </div>
          </article>
        );
      })}
    </div>
  );
}
