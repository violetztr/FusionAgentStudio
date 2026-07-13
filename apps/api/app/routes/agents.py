from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.agent import AgentCreate, AgentKnowledgeBindingCreate, AgentOut, AgentUpdate
from app.services.agent.agent_service import AgentService


router = APIRouter(prefix="/api/agents", tags=["agents"])


def get_agent_service(db: Session = Depends(get_db)) -> AgentService:
    return AgentService(db)


@router.get("", response_model=list[AgentOut])
def list_agents(workspace_id: UUID, service: AgentService = Depends(get_agent_service)):
    return service.list(workspace_id)


@router.post("", response_model=AgentOut)
def create_agent(payload: AgentCreate, workspace_id: UUID, service: AgentService = Depends(get_agent_service)):
    return service.create(workspace_id, payload)


@router.get("/{agent_id}", response_model=AgentOut)
def get_agent(agent_id: UUID, service: AgentService = Depends(get_agent_service)):
    agent = service.get(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.patch("/{agent_id}", response_model=AgentOut)
def update_agent(agent_id: UUID, payload: AgentUpdate, service: AgentService = Depends(get_agent_service)):
    agent = service.update(agent_id, payload)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.delete("/{agent_id}")
def delete_agent(agent_id: UUID, service: AgentService = Depends(get_agent_service)):
    deleted = service.delete(agent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"deleted": True}


@router.post("/{agent_id}/knowledge-bases")
def bind_knowledge_base(
    agent_id: UUID,
    payload: AgentKnowledgeBindingCreate,
    service: AgentService = Depends(get_agent_service),
):
    bound = service.bind_knowledge_base(agent_id, payload.knowledge_base_id)
    if not bound:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"bound": True}


@router.delete("/{agent_id}/knowledge-bases/{knowledge_base_id}")
def unbind_knowledge_base(
    agent_id: UUID,
    knowledge_base_id: UUID,
    service: AgentService = Depends(get_agent_service),
):
    service.unbind_knowledge_base(agent_id, knowledge_base_id)
    return {"unbound": True}


@router.post("/{agent_id}/publish", response_model=AgentOut)
def publish_agent(agent_id: UUID, service: AgentService = Depends(get_agent_service)):
    agent = service.publish(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.post("/{agent_id}/unpublish", response_model=AgentOut)
def unpublish_agent(agent_id: UUID, service: AgentService = Depends(get_agent_service)):
    agent = service.unpublish(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent
