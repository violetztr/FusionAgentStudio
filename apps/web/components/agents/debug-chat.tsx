"use client";

import { FormEvent, useState, useTransition } from "react";

import { apiPost } from "@/lib/api";
import type { ChatResponse } from "@/lib/types";

import { CitationList } from "./citation-list";
import { TracePanel } from "./trace-panel";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  citations?: Array<Record<string, unknown>>;
};

export function DebugChat({ agentId }: { agentId: string }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [latest, setLatest] = useState<ChatResponse | null>(null);
  const [isPending, startTransition] = useTransition();

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = input.trim();
    if (!message || isPending) {
      return;
    }

    setInput("");
    setMessages((current) => [...current, { role: "user", content: message }]);

    startTransition(async () => {
      const response = await apiPost<ChatResponse>(`/api/agents/${agentId}/debug-chat`, { message });
      setLatest(response);
      setMessages((current) => [
        ...current,
        { role: "assistant", content: response.answer, citations: response.citations },
      ]);
    });
  }

  return (
    <div className="debug-grid">
      <section className="panel">
        <h2 className="panel-title">Debug Chat</h2>
        <div className="chat-thread">
          {messages.length === 0 ? (
            <div className="empty">No debug messages yet.</div>
          ) : (
            messages.map((message, index) => (
              <article className="message" data-role={message.role} key={`${message.role}-${index}`}>
                <div className="message-role">{message.role}</div>
                <div>{message.content}</div>
                <CitationList citations={message.citations ?? []} />
              </article>
            ))
          )}
        </div>
        <form className="chat-composer" onSubmit={submit}>
          <textarea
            className="textarea"
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask this agent a grounded question"
            value={input}
          />
          <button className="button" disabled={isPending} type="submit">
            {isPending ? "Sending" : "Send"}
          </button>
        </form>
      </section>
      <TracePanel citations={latest?.citations ?? []} usage={latest?.usage ?? {}} />
    </div>
  );
}
