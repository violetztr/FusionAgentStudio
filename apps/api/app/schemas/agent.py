from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AgentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = ""
    system_prompt: str = Field(min_length=1)
    model_provider: str = "openai_compatible"
    model_name: str = "gpt-4.1-mini"
    temperature: float = 0.2
    top_k: int = 8
    citation_required: bool = True


class AgentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    system_prompt: str | None = Field(default=None, min_length=1)
    model_name: str | None = None
    temperature: float | None = None
    top_k: int | None = None
    citation_required: bool | None = None


class AgentOut(BaseModel):
    id: UUID
    workspace_id: UUID
    name: str
    description: str
    system_prompt: str
    model_provider: str
    model_name: str
    temperature: float
    top_k: int
    citation_required: bool
    is_published: bool
    public_id: str

    model_config = ConfigDict(from_attributes=True)


class AgentKnowledgeBindingCreate(BaseModel):
    knowledge_base_id: UUID


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: UUID | None = None


class ChatResponse(BaseModel):
    conversation_id: UUID
    answer: str
    citations: list[dict]
    usage: dict
