from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RetrievalCandidate:
    chunk_id: UUID
    source_id: UUID
    knowledge_base_id: UUID
    content: str
    source_title: str
    chunk_index: int
    vector_score: float
    keyword_score: float


@dataclass(frozen=True)
class RetrievalResult:
    chunk_id: UUID
    source_id: UUID
    source_title: str
    chunk_index: int
    content: str
    score: float
