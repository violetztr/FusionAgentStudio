"use client";

import { FormEvent, useState, useTransition } from "react";

import { CitationList } from "@/components/agents/citation-list";
import { apiPost } from "@/lib/api";
import type { ChatResponse, PublicAgent } from "@/lib/types";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  citations?: Array<Record<string, unknown>>;
};

export function PublicChat({ agent }: { agent: PublicAgent }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [input, setInput] = useState("");
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
      const response = await apiPost<ChatResponse>(`/api/public/agents/${agent.public_id}/chat`, {
        conversation_id: conversationId,
        message,
      });
      setConversationId(response.conversation_id);
      setMessages((current) => [
        ...current,
        { role: "assistant", content: response.answer, citations: response.citations },
      ]);
    });
  }

  return (
    <section className="panel">
      <div className="chat-thread">
        {messages.length === 0 ? (
          <div className="empty">No messages yet.</div>
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
          placeholder={`Ask ${agent.name}`}
          value={input}
        />
        <button className="button" disabled={isPending} type="submit">
          {isPending ? "Sending" : "Send"}
        </button>
      </form>
    </section>
  );
}
