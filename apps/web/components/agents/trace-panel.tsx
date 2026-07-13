import { formatUsage } from "@/lib/usage";

export function TracePanel({
  citations,
  usage,
}: {
  citations: Array<Record<string, unknown>>;
  usage: Record<string, unknown>;
}) {
  return (
    <aside className="panel">
      <h2 className="panel-title">Trace</h2>
      <div className="trace-stack">
        <div className="status-line">
          <span className="row-meta">Retrieved chunks</span>
          <span className="pill" data-tone="neutral">
            {citations.length}
          </span>
        </div>
        <div className="status-line">
          <span className="row-meta">Model usage</span>
          <span className="pill" data-tone="neutral">
            {formatUsage(usage)}
          </span>
        </div>
      </div>
    </aside>
  );
}
