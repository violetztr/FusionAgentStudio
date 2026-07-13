"use client";

import { FormEvent, useState, useTransition } from "react";
import { useRouter } from "next/navigation";

import { createWebSource } from "@/lib/source-api";

export function WebSourceForm({ knowledgeBaseId }: { knowledgeBaseId: string }) {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");
  const [isPending, startTransition] = useTransition();

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextUrl = url.trim();
    const nextTitle = title.trim() || nextUrl;
    if (!nextUrl || isPending) {
      return;
    }

    setError("");
    startTransition(async () => {
      try {
        await createWebSource(knowledgeBaseId, { title: nextTitle, url: nextUrl });
        setTitle("");
        setUrl("");
        router.refresh();
      } catch {
        setError("Failed to add web source.");
      }
    });
  }

  return (
    <form className="panel" onSubmit={submit}>
      <h2 className="panel-title">Web Source</h2>
      <div className="field-stack">
        <input
          className="input"
          name="title"
          onChange={(event) => setTitle(event.target.value)}
          placeholder="Source title"
          type="text"
          value={title}
        />
        <input
          className="input"
          name="url"
          onChange={(event) => setUrl(event.target.value)}
          placeholder="https://example.com/guide"
          type="url"
          value={url}
        />
        {error ? <div className="row-meta">{error}</div> : null}
        <button className="button" disabled={isPending} type="submit">
          {isPending ? "Importing" : "Import URL"}
        </button>
      </div>
    </form>
  );
}
