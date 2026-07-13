import type { Agent } from "@/lib/types";

export function ModelSettings({ agent }: { agent: Agent | null }) {
  return (
    <form className="panel">
      <h2 className="panel-title">Model Settings</h2>
      <div className="field-stack">
        <label className="field-label">
          Model
          <input className="input" defaultValue={agent?.model_name ?? "gpt-4.1-mini"} name="model_name" />
        </label>
        <label className="field-label">
          Temperature
          <div className="range-row">
            <input
              className="input"
              defaultValue={agent?.temperature ?? 0.2}
              max={2}
              min={0}
              name="temperature"
              step={0.1}
              type="number"
            />
            <span className="pill" data-tone="neutral">
              0-2
            </span>
          </div>
        </label>
        <label className="field-label">
          Top-K Retrieval
          <input className="input" defaultValue={agent?.top_k ?? 8} max={20} min={1} name="top_k" type="number" />
        </label>
        <label className="toggle-row">
          <input defaultChecked={agent?.citation_required ?? true} name="citation_required" type="checkbox" />
          Require citations
        </label>
      </div>
    </form>
  );
}
