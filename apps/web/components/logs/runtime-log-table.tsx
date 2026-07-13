import { formatUsage } from "@/lib/usage";
import type { RuntimeLog } from "@/lib/types";

export function RuntimeLogTable({ logs }: { logs: RuntimeLog[] }) {
  if (logs.length === 0) {
    return <div className="empty">No runtime logs yet.</div>;
  }

  return (
    <div className="table">
      <div className="table-row table-head">
        <span>Conversation</span>
        <span>Channel</span>
        <span>Citations</span>
        <span>Usage</span>
      </div>
      {logs.map((log) => (
        <article className="table-row" key={log.conversation_id}>
          <div>
            <div className="row-title">{log.agent_name}</div>
            <div className="row-meta">{log.last_question || "No user question"}</div>
            <div className="row-meta">{log.last_answer || "No assistant answer"}</div>
          </div>
          <span>{log.channel}</span>
          <span>{log.citation_count}</span>
          <span>{formatUsage(log.usage)}</span>
        </article>
      ))}
    </div>
  );
}
