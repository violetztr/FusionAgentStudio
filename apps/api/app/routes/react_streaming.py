"""Server-Sent Events (SSE) streaming route for ReAct agent chat."""

import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.models import Agent
from app.db.session import get_db
from app.schemas.agent import ChatRequest
from app.services.agent_runtime.react_streaming import run_react_loop_streaming
from app.services.model_gateway.factory import get_model_gateway
from app.services.retrieval.service import RetrievalService
from app.services.tools.builtin import build_default_registry

router = APIRouter(tags=["streaming"])


@router.post("/api/agents/{agent_id}/react-chat/stream")
async def react_chat_stream(
    agent_id: UUID,
    payload: ChatRequest,
    db: Session = Depends(get_db),
):
    """Streaming ReAct agent chat via SSE.

    Events emitted:
        thought   – agent is analyzing the request
        action    – agent is calling a tool
        observation – tool result received
        final_answer – agent's final answer
        done      – complete summary with all steps
        error     – error occurred
    """
    agent = db.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    retrieval_service = RetrievalService(db)

    async def bound_search(query: str, top_k: int) -> str:
        results = retrieval_service.retrieve_for_agent(agent.id, query, top_k)
        if not results:
            return "No relevant knowledge found in the bound knowledge bases."
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"[{i}] Source: {r.source_title} (chunk {r.chunk_index})\n{r.content}")
        return "\n\n".join(lines)

    registry = build_default_registry(knowledge_search_handler=bound_search)
    gateway = get_model_gateway()

    async def event_stream():
        try:
            async for event in run_react_loop_streaming(
                gateway=gateway,
                registry=registry,
                user_message=payload.message,
                model=agent.model_name,
                temperature=float(agent.temperature),
                system_prompt=agent.system_prompt,
            ):
                yield f"event: {event['event']}\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n"
        except Exception as exc:
            yield f"event: error\ndata: {json.dumps({'content': str(exc)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
