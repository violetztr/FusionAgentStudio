from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeBaseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = ""


class KnowledgeBaseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None


class KnowledgeBaseOut(BaseModel):
    id: UUID
    workspace_id: UUID
    name: str
    description: str

    model_config = ConfigDict(from_attributes=True)
