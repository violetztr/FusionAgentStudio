"""ReAct agent chat route (synchronous version)."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.agent import ChatRequest
from app.services.agent_runtime.react_chat_service import ReactChatService

router = APIRouter(tags=["react-chat"])


def get_react_chat_service(db: Session = Depends(get_db)) -> ReactChatService:
    return ReactChatService(db)


@router.post("/api/agents/{agent_id}/react-chat")
async def react_chat(
    agent_id: UUID,
    payload: ChatRequest,
    service: ReactChatService = Depends(get_react_chat_service),
):
    try:
        return await service.execute(
            agent_id=agent_id,
            message=payload.message,
            conversation_id=payload.conversation_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
