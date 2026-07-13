# Knowledge Fusion Agent Studio Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a multi-knowledge-source agent builder platform where users can ingest documents, web pages, notes, and API knowledge, then create configurable agents that search, reason, answer with citations, and publish as chat experiences.

**Architecture:** Use a decoupled full-stack architecture: Next.js for the builder UI, FastAPI for product APIs, PostgreSQL with pgvector for relational and vector storage, Redis/Celery for ingestion jobs, and a model gateway for LLM, embedding, and rerank providers. Keep RAG, agent runtime, tool execution, and UI concerns separated so the platform can evolve from a single-user MVP into a team product.

**Tech Stack:** Next.js, React, TypeScript, FastAPI, Python, PostgreSQL, pgvector, Redis, Celery, SQLAlchemy, Alembic, Pydantic, OpenAI-compatible model APIs, PyMuPDF, python-docx, trafilatura, pytest, Playwright.

---

## MVP Scope

- Single workspace with local authentication.
- Knowledge sources: PDF, DOCX, TXT, Markdown, web URL, manual note.
- Knowledge fusion: vector search, keyword search, hybrid merge, rerank-ready interface, citation mapping.
- Agent builder: role, system prompt, model settings, bound knowledge bases, answer rules.
- Runtime: chat, retrieval, answer generation, citations, trace logging.
- Publish: shareable chat page with access token.
- Observability: ingestion status, runtime traces, retrieval chunks, model usage.

## Core Runtime Flows

### Ingestion

1. Create a source record with `pending` status.
2. Store uploaded file, URL, or note payload.
3. Parse source into raw text.
4. Clean text.
5. Split text into stable chunks.
6. Generate embeddings.
7. Store chunks, metadata, hashes, and vectors.
8. Mark source as `indexed` or `failed`.

### Retrieval

1. Load agent-bound knowledge bases.
2. Embed the user query.
3. Run vector search and keyword search.
4. Merge and deduplicate results.
5. Select top chunks.
6. Build citation payloads.
7. Record retrieval trace.

### Agent Answer

1. Load agent configuration.
2. Retrieve relevant knowledge.
3. Build grounded prompt.
4. Call model gateway.
5. Save messages, citations, usage, and traces.
6. Return answer with citations.

## Recommended Tasks

- [ ] Task 1: Repository scaffold.
- [ ] Task 2: Backend foundation and health check.
- [ ] Task 3: Database models and migrations.
- [ ] Task 4: Knowledge base API.
- [ ] Task 5: Source ingestion pipeline.
- [ ] Task 6: Model gateway.
- [ ] Task 7: Retrieval service.
- [ ] Task 8: Agent runtime.
- [ ] Task 9: Agent API and debug chat.
- [ ] Task 10: Frontend foundation.
- [ ] Task 11: Knowledge source UI.
- [ ] Task 12: Agent builder UI.
- [ ] Task 13: Debug chat UI.
- [ ] Task 14: Published chat page.
- [ ] Task 15: Runtime logs and evaluation seeds.

## Acceptance Criteria

- A user can create a knowledge base.
- A user can add PDF, DOCX, TXT, Markdown, web URL, and manual note sources.
- Sources move through `pending`, `processing`, `indexed`, and `failed` statuses correctly.
- Indexed chunks are stored with content, metadata, and embeddings.
- A user can create an agent and bind one or more knowledge bases.
- The debug chat answers questions using retrieved chunks.
- Answers include citations when citation mode is enabled.
- Debug trace shows retrieved chunks and model usage.
- A user can publish an agent.
- Published chat can answer through the same runtime path.
- Tests cover chunking, cleaning, model gateway contract, hybrid retrieval merge, prompt construction, citations, agent CRUD, debug chat, and public chat.
