import type { Agent } from "@/lib/types";

export function AgentForm({ agent }: { agent: Agent | null }) {
  return (
    <form className="panel">
      <h2 className="panel-title">Agent Profile</h2>
      <div className="field-stack">
        <label className="field-label">
          Name
          <input className="input" defaultValue={agent?.name ?? ""} name="name" placeholder="Product Assistant" />
        </label>
        <label className="field-label">
          Description
          <input
            className="input"
            defaultValue={agent?.description ?? ""}
            name="description"
            placeholder="Answers questions from product knowledge"
          />
        </label>
        <label className="field-label">
          System Prompt
          <textarea
            className="textarea"
            defaultValue={agent?.system_prompt ?? ""}
            name="system_prompt"
            placeholder="Answer using bound knowledge and include citations."
          />
        </label>
        <button className="button" type="button">
          Save Profile
        </button>
      </div>
    </form>
  );
}
