import { NoteSourceForm } from "@/components/knowledge/note-source-form";
import { SourceStatusList } from "@/components/knowledge/source-status-list";
import { SourceUpload } from "@/components/knowledge/source-upload";
import { WebSourceForm } from "@/components/knowledge/web-source-form";
import { apiGet } from "@/lib/api";
import type { KnowledgeBase, KnowledgeSource } from "@/lib/types";

export default async function KnowledgeBaseDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [knowledgeBase, sources] = await Promise.all([loadKnowledgeBase(id), loadSources(id)]);

  return (
    <>
      <header className="page-header">
        <div>
          <span className="eyebrow">Knowledge Base</span>
          <h1 className="page-title">{knowledgeBase?.name ?? "Knowledge Base"}</h1>
          <p className="page-subtitle">{knowledgeBase?.description || "Manage source material and indexing status."}</p>
        </div>
      </header>

      <div className="source-grid">
        <SourceUpload />
        <WebSourceForm knowledgeBaseId={id} />
        <NoteSourceForm knowledgeBaseId={id} />
      </div>

      <section className="section">
        <SourceStatusList sources={sources} />
      </section>
    </>
  );
}

async function loadKnowledgeBase(id: string) {
  try {
    return await apiGet<KnowledgeBase>(`/api/knowledge-bases/${id}`);
  } catch {
    return null;
  }
}

async function loadSources(id: string) {
  try {
    return await apiGet<KnowledgeSource[]>(`/api/knowledge-bases/${id}/sources`);
  } catch {
    return [];
  }
}
