import type { Agent } from "@/lib/types";

export function PublishControls({ agent }: { agent: Agent | null }) {
  return (
    <section className="panel">
      <h2 className="panel-title">Publish</h2>
      <div className="status-line">
        <span className="row-meta">Current status</span>
        <span className="pill">{agent?.is_published ? "Published" : "Draft"}</span>
      </div>
      <div className="field-stack" style={{ marginTop: 14 }}>
        <input className="input" readOnly value={agent?.public_id ?? "Not published"} />
        <button className="button" type="button">
          {agent?.is_published ? "Unpublish" : "Publish"}
        </button>
      </div>
    </section>
  );
}
