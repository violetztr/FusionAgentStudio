from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.agent import ChatRequest, ChatResponse
from app.services.agent_runtime.chat_service import ChatService


router = APIRouter(tags=["chat"])


def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    return ChatService(db)


@router.post("/api/agents/{agent_id}/debug-chat", response_model=ChatResponse)
def debug_chat(agent_id: UUID, payload: ChatRequest, service: ChatService = Depends(get_chat_service)):
    try:
        return service.execute(
            agent_id=agent_id,
            message=payload.message,
            channel="debug",
            conversation_id=payload.conversation_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
