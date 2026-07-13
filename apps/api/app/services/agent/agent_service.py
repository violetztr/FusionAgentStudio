import secrets
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import Agent, AgentKnowledgeBinding
from app.schemas.agent import AgentCreate, AgentUpdate


class AgentService:
    def __init__(self, db: Session):
        self.db = db

    def list(self, workspace_id: UUID) -> list[Agent]:
        return self.db.query(Agent).filter(Agent.workspace_id == workspace_id).order_by(Agent.created_at.desc()).all()

    def create(self, workspace_id: UUID, payload: AgentCreate) -> Agent:
        agent = Agent(
            workspace_id=workspace_id,
            name=payload.name,
            description=payload.description,
            system_prompt=payload.system_prompt,
            model_provider=payload.model_provider,
            model_name=payload.model_name,
            temperature=payload.temperature,
            top_k=payload.top_k,
            citation_required=payload.citation_required,
            is_published=False,
            public_id=secrets.token_urlsafe(12),
        )
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def get(self, agent_id: UUID) -> Agent | None:
        return self.db.get(Agent, agent_id)

    def update(self, agent_id: UUID, payload: AgentUpdate) -> Agent | None:
        agent = self.get(agent_id)
        if agent is None:
            return None
        for field in ["name", "description", "system_prompt", "model_name", "temperature", "top_k", "citation_required"]:
            value = getattr(payload, field)
            if value is not None:
                setattr(agent, field, value)
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def delete(self, agent_id: UUID) -> bool:
        agent = self.get(agent_id)
        if agent is None:
            return False
        self.db.delete(agent)
        self.db.commit()
        return True

    def bind_knowledge_base(self, agent_id: UUID, knowledge_base_id: UUID) -> bool:
        if self.get(agent_id) is None:
            return False
        existing = (
            self.db.query(AgentKnowledgeBinding)
            .filter(
                AgentKnowledgeBinding.agent_id == agent_id,
                AgentKnowledgeBinding.knowledge_base_id == knowledge_base_id,
            )
            .one_or_none()
        )
        if existing is None:
            self.db.add(AgentKnowledgeBinding(agent_id=agent_id, knowledge_base_id=knowledge_base_id))
            self.db.commit()
        return True

    def unbind_knowledge_base(self, agent_id: UUID, knowledge_base_id: UUID) -> bool:
        binding = (
            self.db.query(AgentKnowledgeBinding)
            .filter(
                AgentKnowledgeBinding.agent_id == agent_id,
                AgentKnowledgeBinding.knowledge_base_id == knowledge_base_id,
            )
            .one_or_none()
        )
        if binding is not None:
            self.db.delete(binding)
            self.db.commit()
        return True

    def publish(self, agent_id: UUID) -> Agent | None:
        agent = self.get(agent_id)
        if agent is None:
            return None
        agent.is_published = True
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def unpublish(self, agent_id: UUID) -> Agent | None:
        agent = self.get(agent_id)
        if agent is None:
            return None
        agent.is_published = False
        self.db.commit()
        self.db.refresh(agent)
        return agent
