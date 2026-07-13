from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import Agent
from app.schemas.agent import ChatResponse, PublicAgentOut
from app.services.agent_runtime.chat_service import ChatService


class PublicChatService:
    def __init__(self, db: Session):
        self.db = db

    def get_public_agent(self, public_id: str) -> PublicAgentOut | None:
        agent = self._load_published_agent(public_id)
        if agent is None:
            return None
        return PublicAgentOut(public_id=agent.public_id, name=agent.name, description=agent.description)

    def execute(self, public_id: str, message: str, conversation_id: UUID | None = None) -> ChatResponse | None:
        agent = self._load_published_agent(public_id)
        if agent is None:
            return None
        return ChatService(self.db).execute(
            agent_id=agent.id,
            message=message,
            channel="published",
            conversation_id=conversation_id,
        )

    def _load_published_agent(self, public_id: str) -> Agent | None:
        return (
            self.db.query(Agent)
            .filter(
                Agent.public_id == public_id,
                Agent.is_published.is_(True),
            )
            .one_or_none()
        )
