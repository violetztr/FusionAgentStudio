"""ReAct chat service – combines Tool Registry + ReAct loop + knowledge retrieval."""

import json
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import Agent, Conversation, Message, RuntimeTrace
from app.services.agent_runtime.react_agent import ReActResult, run_react_loop
from app.services.model_gateway.factory import get_model_gateway
from app.services.retrieval.service import RetrievalService
from app.services.tools.builtin import build_default_registry


async def _knowledge_search_handler(query: str, top_k: int) -> str:
    """Adapter: knowledge search that is injected into the tool registry at request time."""
    # This is a placeholder – the actual handler uses the DB session
    raise RuntimeError("knowledge_search_handler must be bound at request time")


class ReactChatService:
    """Chat service that uses the ReAct agent loop with tool calling."""

    def __init__(self, db: Session):
        self.db = db

    async def execute(self, agent_id: UUID, message: str, conversation_id: UUID | None = None) -> dict:
        agent = self.db.get(Agent, agent_id)
        if agent is None:
            raise ValueError("Agent not found")

        # Persist conversation
        conversation = self._load_or_create_conversation(agent, "react", conversation_id)
        user_message = Message(conversation_id=conversation.id, role="user", content=message)
        self.db.add(user_message)
        self.db.flush()

        # Build tool registry with knowledge search bound to this agent
        retrieval_service = RetrievalService(self.db)

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

        result: ReActResult = await run_react_loop(
            gateway=gateway,
            registry=registry,
            user_message=message,
            model=agent.model_name,
            temperature=float(agent.temperature),
            system_prompt=agent.system_prompt,
        )

        # Persist assistant message
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=result.final_answer,
            usage=result.usage,
        )
        self.db.add(assistant_message)
        self.db.flush()

        # Persist traces
        self.db.add(
            RuntimeTrace(
                conversation_id=conversation.id,
                message_id=assistant_message.id,
                agent_id=agent.id,
                trace_type="react_loop",
                payload={
                    "total_tool_calls": result.total_tool_calls,
                    "total_iterations": result.total_iterations,
                    "steps": [
                        {
                            "step_type": s.step_type,
                            "content": s.content,
                            "tool_name": s.tool_name,
                            "tool_input": s.tool_input,
                            "tool_result": s.tool_result,
                        }
                        for s in result.steps
                    ],
                },
            )
        )

        self.db.commit()

        return {
            "conversation_id": str(conversation.id),
            "answer": result.final_answer,
            "usage": result.usage,
            "total_tool_calls": result.total_tool_calls,
            "total_iterations": result.total_iterations,
            "steps": [
                {
                    "step_type": s.step_type,
                    "content": s.content,
                    "tool_name": s.tool_name,
                    "tool_input": s.tool_input,
                    "tool_result": s.tool_result,
                }
                for s in result.steps
            ],
        }

    def _load_or_create_conversation(self, agent: Agent, channel: str, conversation_id: UUID | None) -> Conversation:
        if conversation_id is not None:
            conversation = self.db.get(Conversation, conversation_id)
            if conversation is not None:
                return conversation
        conversation = Conversation(agent_id=agent.id, workspace_id=agent.workspace_id, channel=channel)
        self.db.add(conversation)
        self.db.flush()
        return conversation
