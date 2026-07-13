from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import KnowledgeBase
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseUpdate


class KnowledgeBaseService:
    def __init__(self, db: Session):
        self.db = db

    def list(self, workspace_id: UUID) -> list[KnowledgeBase]:
        return (
            self.db.query(KnowledgeBase)
            .filter(KnowledgeBase.workspace_id == workspace_id)
            .order_by(KnowledgeBase.created_at.desc())
            .all()
        )

    def create(self, workspace_id: UUID, payload: KnowledgeBaseCreate) -> KnowledgeBase:
        knowledge_base = KnowledgeBase(
            workspace_id=workspace_id,
            name=payload.name,
            description=payload.description,
        )
        self.db.add(knowledge_base)
        self.db.commit()
        self.db.refresh(knowledge_base)
        return knowledge_base

    def get(self, knowledge_base_id: UUID) -> KnowledgeBase | None:
        return self.db.get(KnowledgeBase, knowledge_base_id)

    def update(self, knowledge_base_id: UUID, payload: KnowledgeBaseUpdate) -> KnowledgeBase | None:
        knowledge_base = self.get(knowledge_base_id)
        if knowledge_base is None:
            return None
        if payload.name is not None:
            knowledge_base.name = payload.name
        if payload.description is not None:
            knowledge_base.description = payload.description
        self.db.commit()
        self.db.refresh(knowledge_base)
        return knowledge_base

    def delete(self, knowledge_base_id: UUID) -> bool:
        knowledge_base = self.get(knowledge_base_id)
        if knowledge_base is None:
            return False
        self.db.delete(knowledge_base)
        self.db.commit()
        return True
