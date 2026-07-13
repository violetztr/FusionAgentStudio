import { afterEach, describe, expect, test, vi } from "vitest";

import { createNoteSource, createWebSource, reindexSource } from "./source-api";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("source api", () => {
  test("createNoteSource posts note payload to a knowledge base", async () => {
    const fetchMock = vi.fn(async () => Response.json({ id: "source-1" }));
    vi.stubGlobal("fetch", fetchMock);

    await createNoteSource("kb-1", { title: "Handbook", content: "Refund policy" });

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/knowledge-bases/kb-1/sources/note",
      expect.objectContaining({
        body: JSON.stringify({ title: "Handbook", content: "Refund policy" }),
        method: "POST",
      }),
    );
  });

  test("createWebSource posts web source payload to a knowledge base", async () => {
    const fetchMock = vi.fn(async () => Response.json({ id: "source-1" }));
    vi.stubGlobal("fetch", fetchMock);

    await createWebSource("kb-1", { title: "Docs", url: "https://example.com/docs" });

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/knowledge-bases/kb-1/sources/web",
      expect.objectContaining({
        body: JSON.stringify({ title: "Docs", url: "https://example.com/docs" }),
        method: "POST",
      }),
    );
  });

  test("reindexSource starts indexing for a source", async () => {
    const fetchMock = vi.fn(async () => Response.json({ indexed: true }));
    vi.stubGlobal("fetch", fetchMock);

    await reindexSource("source-1");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/sources/source-1/reindex",
      expect.objectContaining({
        body: JSON.stringify({}),
        method: "POST",
      }),
    );
  });
});
