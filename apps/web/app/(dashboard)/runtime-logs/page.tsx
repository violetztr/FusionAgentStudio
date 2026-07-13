import { RuntimeLogTable } from "@/components/logs/runtime-log-table";
import { apiGet } from "@/lib/api";
import type { RuntimeLog } from "@/lib/types";

export default async function RuntimeLogsPage() {
  const logs = await loadRuntimeLogs();

  return (
    <>
      <header className="page-header">
        <div>
          <span className="eyebrow">Observability</span>
          <h1 className="page-title">Runtime Logs</h1>
          <p className="page-subtitle">Recent conversations, citation counts, and model usage from debug and published agents.</p>
        </div>
      </header>
      <section className="section">
        <RuntimeLogTable logs={logs} />
      </section>
    </>
  );
}

async function loadRuntimeLogs() {
  try {
    return await apiGet<RuntimeLog[]>("/api/runtime-logs");
  } catch {
    return [];
  }
}
