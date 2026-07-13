from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseOut, KnowledgeBaseUpdate
from app.services.knowledge.knowledge_base_service import KnowledgeBaseService


router = APIRouter(prefix="/api/knowledge-bases", tags=["knowledge-bases"])


def get_knowledge_base_service(db: Session = Depends(get_db)) -> KnowledgeBaseService:
    return KnowledgeBaseService(db)


@router.get("", response_model=list[KnowledgeBaseOut])
def list_knowledge_bases(
    workspace_id: UUID,
    service: KnowledgeBaseService = Depends(get_knowledge_base_service),
):
    return service.list(workspace_id)


@router.post("", response_model=KnowledgeBaseOut)
def create_knowledge_base(
    payload: KnowledgeBaseCreate,
    workspace_id: UUID,
    service: KnowledgeBaseService = Depends(get_knowledge_base_service),
):
    return service.create(workspace_id, payload)


@router.get("/{knowledge_base_id}", response_model=KnowledgeBaseOut)
def get_knowledge_base(
    knowledge_base_id: UUID,
    service: KnowledgeBaseService = Depends(get_knowledge_base_service),
):
    knowledge_base = service.get(knowledge_base_id)
    if knowledge_base is None:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return knowledge_base


@router.patch("/{knowledge_base_id}", response_model=KnowledgeBaseOut)
def update_knowledge_base(
    knowledge_base_id: UUID,
    payload: KnowledgeBaseUpdate,
    service: KnowledgeBaseService = Depends(get_knowledge_base_service),
):
    knowledge_base = service.update(knowledge_base_id, payload)
    if knowledge_base is None:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return knowledge_base


@router.delete("/{knowledge_base_id}")
def delete_knowledge_base(
    knowledge_base_id: UUID,
    service: KnowledgeBaseService = Depends(get_knowledge_base_service),
):
    deleted = service.delete(knowledge_base_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return {"deleted": True}
