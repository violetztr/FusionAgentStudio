"use client";

import { FormEvent, useState, useTransition } from "react";
import { useRouter } from "next/navigation";

import { createNoteSource } from "@/lib/source-api";

export function NoteSourceForm({ knowledgeBaseId }: { knowledgeBaseId: string }) {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [error, setError] = useState("");
  const [isPending, startTransition] = useTransition();

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextTitle = title.trim();
    const nextContent = content.trim();
    if (!nextTitle || !nextContent || isPending) {
      return;
    }

    setError("");
    startTransition(async () => {
      try {
        await createNoteSource(knowledgeBaseId, { title: nextTitle, content: nextContent });
        setTitle("");
        setContent("");
        router.refresh();
      } catch {
        setError("Failed to add note source.");
      }
    });
  }

  return (
    <form className="panel" onSubmit={submit}>
      <h2 className="panel-title">Manual Note</h2>
      <div className="field-stack">
        <input
          className="input"
          name="title"
          onChange={(event) => setTitle(event.target.value)}
          placeholder="Note title"
          type="text"
          value={title}
        />
        <textarea
          className="textarea"
          name="content"
          onChange={(event) => setContent(event.target.value)}
          placeholder="Paste knowledge text"
          value={content}
        />
        {error ? <div className="row-meta">{error}</div> : null}
        <button className="button" disabled={isPending} type="submit">
          {isPending ? "Adding" : "Add Note"}
        </button>
      </div>
    </form>
  );
}
