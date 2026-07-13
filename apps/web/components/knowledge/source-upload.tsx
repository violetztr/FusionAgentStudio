"use client";

import { FormEvent, useRef, useState, useTransition } from "react";
import { useRouter } from "next/navigation";

import { createFileSource } from "@/lib/source-api";

export function SourceUpload({ knowledgeBaseId }: { knowledgeBaseId: string }) {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [title, setTitle] = useState("");
  const [error, setError] = useState("");
  const [isPending, startTransition] = useTransition();

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const file = fileInputRef.current?.files?.[0];
    if (!file || isPending) {
      return;
    }

    setError("");
    startTransition(async () => {
      try {
        await createFileSource(knowledgeBaseId, { title: title.trim() || file.name, file });
        setTitle("");
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
        router.refresh();
      } catch {
        setError("Failed to upload file source.");
      }
    });
  }

  return (
    <form className="panel" onSubmit={submit}>
      <h2 className="panel-title">File Source</h2>
      <div className="field-stack">
        <input
          className="input"
          name="title"
          onChange={(event) => setTitle(event.target.value)}
          placeholder="Source title"
          type="text"
          value={title}
        />
        <input className="input" name="file" ref={fileInputRef} type="file" />
        {error ? <div className="row-meta">{error}</div> : null}
        <button className="button" disabled={isPending} type="submit">
          {isPending ? "Uploading" : "Upload"}
        </button>
      </div>
    </form>
  );
}
