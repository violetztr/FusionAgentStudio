# Knowledge Fusion Agent Studio

Knowledge Fusion Agent Studio is a multi-knowledge-source agent builder platform. The MVP focuses on ingesting documents, web pages, and notes into knowledge bases, binding those knowledge bases to configurable agents, and debugging grounded answers with citations and runtime traces.

## Planned Stack

- Frontend: Next.js, React, TypeScript
- Backend: FastAPI, Python, SQLAlchemy, Alembic
- Storage: PostgreSQL with pgvector
- Jobs: Redis and Celery
- Models: OpenAI-compatible chat and embedding APIs

## Local Services

```bash
docker compose up -d postgres redis
```

## Development Commands

```bash
pnpm dev:web
pnpm dev:api
pnpm test:web
pnpm test:api
```

## Project Plan

The implementation plan lives in `docs/superpowers/plans/2026-07-13-knowledge-fusion-agent-studio.md`.
