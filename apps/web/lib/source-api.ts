import { apiPost } from "./api";
import type { KnowledgeSource } from "./types";

type NoteSourcePayload = {
  title: string;
  content: string;
};

type WebSourcePayload = {
  title: string;
  url: string;
};

type FileSourcePayload = {
  title: string;
  file: File;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export function createNoteSource(knowledgeBaseId: string, payload: NoteSourcePayload) {
  return apiPost<KnowledgeSource>(`/api/knowledge-bases/${knowledgeBaseId}/sources/note`, payload);
}

export function createWebSource(knowledgeBaseId: string, payload: WebSourcePayload) {
  return apiPost<KnowledgeSource>(`/api/knowledge-bases/${knowledgeBaseId}/sources/web`, payload);
}

export async function createFileSource(knowledgeBaseId: string, payload: FileSourcePayload) {
  const formData = new FormData();
  formData.append("title", payload.title);
  formData.append("file", payload.file);

  const response = await fetch(`${API_BASE_URL}/api/knowledge-bases/${knowledgeBaseId}/sources/file`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) {
    throw new Error(`POST file source failed with ${response.status}`);
  }
  return response.json() as Promise<KnowledgeSource>;
}

export function reindexSource(sourceId: string) {
  return apiPost<{ indexed: true }>(`/api/sources/${sourceId}/reindex`, {});
}
