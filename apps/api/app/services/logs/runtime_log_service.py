from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import Agent, Conversation, Message, RuntimeTrace


class RuntimeLogService:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[dict]:
        conversations = self.db.query(Conversation).order_by(Conversation.created_at.desc()).limit(50).all()
        rows = []
        for conversation in conversations:
            agent = self.db.get(Agent, conversation.agent_id)
            messages = (
                self.db.query(Message)
                .filter(Message.conversation_id == conversation.id)
                .order_by(Message.created_at.asc())
                .all()
            )
            user_messages = [message for message in messages if message.role == "user"]
            assistant_messages = [message for message in messages if message.role == "assistant"]
            last_question = user_messages[-1].content if user_messages else ""
            last_answer = assistant_messages[-1].content if assistant_messages else ""
            citations = assistant_messages[-1].citations if assistant_messages else []
            usage = assistant_messages[-1].usage if assistant_messages else {}
            rows.append(
                {
                    "conversation_id": conversation.id,
                    "agent_name": agent.name if agent else "Unknown Agent",
                    "channel": conversation.channel,
                    "message_count": len(messages),
                    "last_question": last_question,
                    "last_answer": last_answer,
                    "citation_count": len(citations),
                    "usage": usage,
                }
            )
        return rows

    def traces(self, conversation_id: UUID) -> list[dict]:
        traces = (
            self.db.query(RuntimeTrace)
            .filter(RuntimeTrace.conversation_id == conversation_id)
            .order_by(RuntimeTrace.created_at.asc())
            .all()
        )
        return [{"trace_type": trace.trace_type, "payload": trace.payload} for trace in traces]
