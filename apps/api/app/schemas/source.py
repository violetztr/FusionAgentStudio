from uuid import UUID

from pydantic import BaseModel, Field


class WebSourceCreate(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    url: str = Field(min_length=1)


class NoteSourceCreate(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    content: str = Field(min_length=1)


class SourceOut(BaseModel):
    id: UUID
    knowledge_base_id: UUID
    source_type: str
    title: str
    uri: str
    storage_path: str
    status: str
    error_message: str
    metadata: dict


class SourceChunkOut(BaseModel):
    id: UUID
    source_id: UUID
    knowledge_base_id: UUID
    chunk_index: int
    content: str
    token_count: int
    metadata: dict
