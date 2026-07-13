import { PublicChat } from "@/components/public/public-chat";
import { apiGet } from "@/lib/api";
import type { PublicAgent } from "@/lib/types";

export default async function PublicChatPage({ params }: { params: Promise<{ publicId: string }> }) {
  const { publicId } = await params;
  const agent = await loadPublicAgent(publicId);

  if (agent === null) {
    return (
      <main className="public-shell">
        <div className="empty">Published agent not found.</div>
      </main>
    );
  }

  return (
    <main className="public-shell">
      <header className="public-header">
        <span className="eyebrow">Published Agent</span>
        <h1 className="page-title">{agent.name}</h1>
        <p className="page-subtitle">{agent.description || "Knowledge-grounded chat"}</p>
      </header>
      <PublicChat agent={agent} />
    </main>
  );
}

async function loadPublicAgent(publicId: string) {
  try {
    return await apiGet<PublicAgent>(`/api/public/agents/${publicId}`);
  } catch {
    return null;
  }
}
