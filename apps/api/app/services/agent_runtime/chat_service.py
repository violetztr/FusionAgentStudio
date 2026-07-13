from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import Agent, Conversation, Message, RuntimeTrace
from app.schemas.agent import ChatResponse
from app.services.agent_runtime.runtime import run_agent_answer
from app.services.model_gateway.factory import get_model_gateway
from app.services.retrieval.service import RetrievalService


class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, agent_id: UUID, message: str, channel: str, conversation_id: UUID | None = None) -> ChatResponse:
        agent = self.db.get(Agent, agent_id)
        if agent is None:
            raise ValueError("Agent not found")

        conversation = self._load_or_create_conversation(agent, channel, conversation_id)
        user_message = Message(conversation_id=conversation.id, role="user", content=message)
        self.db.add(user_message)
        self.db.flush()

        retrieval_results = RetrievalService(self.db).retrieve_for_agent(agent.id, message, int(agent.top_k))
        runtime_result = run_agent_answer(
            gateway=get_model_gateway(),
            agent_prompt=agent.system_prompt,
            question=message,
            model_name=agent.model_name,
            temperature=float(agent.temperature),
            citation_required=agent.citation_required,
            retrieval_results=retrieval_results,
        )
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=runtime_result.answer,
            citations=runtime_result.citations,
            usage=runtime_result.usage,
        )
        self.db.add(assistant_message)
        self.db.flush()
        self.db.add(
            RuntimeTrace(
                conversation_id=conversation.id,
                message_id=assistant_message.id,
                agent_id=agent.id,
                trace_type="retrieval",
                payload={
                    "query": message,
                    "chunks": [
                        {
                            "chunk_id": str(result.chunk_id),
                            "source_id": str(result.source_id),
                            "source_title": result.source_title,
                            "chunk_index": result.chunk_index,
                            "score": result.score,
                        }
                        for result in retrieval_results
                    ],
                },
            )
        )
        self.db.add(
            RuntimeTrace(
                conversation_id=conversation.id,
                message_id=assistant_message.id,
                agent_id=agent.id,
                trace_type="final_answer",
                payload={
                    "answer": runtime_result.answer,
                    "citations": runtime_result.citations,
                    "usage": runtime_result.usage,
                },
            )
        )
        self.db.commit()
        return ChatResponse(
            conversation_id=conversation.id,
            answer=runtime_result.answer,
            citations=runtime_result.citations,
            usage=runtime_result.usage,
        )

    def _load_or_create_conversation(self, agent: Agent, channel: str, conversation_id: UUID | None) -> Conversation:
        if conversation_id is not None:
            conversation = self.db.get(Conversation, conversation_id)
            if conversation is not None:
                return conversation

        conversation = Conversation(agent_id=agent.id, workspace_id=agent.workspace_id, channel=channel)
        self.db.add(conversation)
        self.db.flush()
        return conversation
