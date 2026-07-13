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

export function createNoteSource(knowledgeBaseId: string, payload: NoteSourcePayload) {
  return apiPost<KnowledgeSource>(`/api/knowledge-bases/${knowledgeBaseId}/sources/note`, payload);
}

export function createWebSource(knowledgeBaseId: string, payload: WebSourcePayload) {
  return apiPost<KnowledgeSource>(`/api/knowledge-bases/${knowledgeBaseId}/sources/web`, payload);
}

export function reindexSource(sourceId: string) {
  return apiPost<{ indexed: true }>(`/api/sources/${sourceId}/reindex`, {});
}
