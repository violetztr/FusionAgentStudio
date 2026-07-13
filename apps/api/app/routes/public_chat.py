from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.agent import ChatRequest, ChatResponse, PublicAgentOut
from app.services.agent_runtime.public_chat_service import PublicChatService


router = APIRouter(prefix="/api/public", tags=["public-chat"])


def get_public_chat_service(db: Session = Depends(get_db)) -> PublicChatService:
    return PublicChatService(db)


@router.get("/agents/{public_id}", response_model=PublicAgentOut)
def get_public_agent(public_id: str, service: PublicChatService = Depends(get_public_chat_service)):
    agent = service.get_public_agent(public_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Published agent not found")
    return agent


@router.post("/agents/{public_id}/chat", response_model=ChatResponse)
def public_agent_chat(
    public_id: str,
    payload: ChatRequest,
    service: PublicChatService = Depends(get_public_chat_service),
):
    response = service.execute(public_id, payload.message, payload.conversation_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Published agent not found")
    return response
