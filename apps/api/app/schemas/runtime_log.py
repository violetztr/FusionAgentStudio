from uuid import UUID

from pydantic import BaseModel


class RuntimeLogOut(BaseModel):
    conversation_id: UUID
    agent_name: str
    channel: str
    message_count: int
    last_question: str
    last_answer: str
    citation_count: int
    usage: dict


class RuntimeTraceOut(BaseModel):
    trace_type: str
    payload: dict
