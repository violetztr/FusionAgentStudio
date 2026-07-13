import { afterEach, describe, expect, test, vi } from "vitest";

import { apiGet, apiPost } from "./api";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("api client", () => {
  test("apiGet returns parsed JSON for successful responses", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => Response.json({ ok: true })),
    );

    await expect(apiGet("/api/health")).resolves.toEqual({ ok: true });
  });

  test("apiPost sends JSON body", async () => {
    const fetchMock = vi.fn(async () => Response.json({ created: true }));
    vi.stubGlobal("fetch", fetchMock);

    await apiPost("/api/items", { name: "Knowledge" });

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/items",
      expect.objectContaining({
        body: JSON.stringify({ name: "Knowledge" }),
        method: "POST",
      }),
    );
  });
});
