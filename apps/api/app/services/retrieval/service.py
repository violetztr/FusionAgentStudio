import math
import re
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import AgentKnowledgeBinding, KnowledgeChunk, KnowledgeSource
from app.services.model_gateway.factory import get_model_gateway
from app.services.model_gateway.types import ModelGateway
from app.services.retrieval.hybrid import merge_retrieval_candidates
from app.services.retrieval.types import RetrievalCandidate, RetrievalResult


def keyword_score(content: str, query: str) -> float:
    terms = set(_terms(query))
    if not terms:
        return 0.0
    content_text = content.lower()
    content_terms = set(_latin_terms(content))
    hits = sum(
        1
        for term in terms
        if (term in content_text if _contains_cjk(term) else term in content_terms)
    )
    return hits / len(terms)


def build_keyword_candidate(
    chunk_id: UUID,
    source_id: UUID,
    knowledge_base_id: UUID,
    content: str,
    source_title: str,
    chunk_index: int,
    query: str,
) -> RetrievalCandidate:
    return RetrievalCandidate(
        chunk_id=chunk_id,
        source_id=source_id,
        knowledge_base_id=knowledge_base_id,
        content=content,
        source_title=source_title,
        chunk_index=chunk_index,
        vector_score=0.0,
        keyword_score=keyword_score(content, query),
    )


class RetrievalService:
    def __init__(self, db: Session, gateway: ModelGateway | None = None):
        self.db = db
        self.gateway = gateway

    def retrieve_for_agent(self, agent_id: UUID, query: str, limit: int) -> list[RetrievalResult]:
        knowledge_base_ids = [
            binding.knowledge_base_id
            for binding in self.db.query(AgentKnowledgeBinding)
            .filter(AgentKnowledgeBinding.agent_id == agent_id)
            .all()
        ]
        if not knowledge_base_ids:
            return []

        chunks = (
            self.db.query(KnowledgeChunk, KnowledgeSource)
            .join(KnowledgeSource, KnowledgeChunk.source_id == KnowledgeSource.id)
            .filter(KnowledgeChunk.knowledge_base_id.in_(knowledge_base_ids))
            .all()
        )

        candidates = [
            build_keyword_candidate(
                chunk_id=chunk.id,
                source_id=chunk.source_id,
                knowledge_base_id=chunk.knowledge_base_id,
                content=chunk.content,
                source_title=source.title,
                chunk_index=chunk.chunk_index,
                query=query,
            )
            for chunk, source in chunks
        ]
        candidates.extend(self._vector_candidates(chunks, query))

        useful_candidates = [
            candidate for candidate in candidates if candidate.keyword_score > 0 or candidate.vector_score > 0
        ]
        return merge_retrieval_candidates(useful_candidates, limit)

    def _vector_candidates(
        self,
        chunks: list[tuple[KnowledgeChunk, KnowledgeSource]],
        query: str,
    ) -> list[RetrievalCandidate]:
        embedded_chunks = [(chunk, source) for chunk, source in chunks if chunk.embedding is not None]
        if not embedded_chunks:
            return []

        try:
            query_embedding = (self.gateway or get_model_gateway()).embed_texts([query])[0]
        except Exception:
            return []

        return [
            RetrievalCandidate(
                chunk_id=chunk.id,
                source_id=chunk.source_id,
                knowledge_base_id=chunk.knowledge_base_id,
                content=chunk.content,
                source_title=source.title,
                chunk_index=chunk.chunk_index,
                vector_score=max(0.0, _cosine_similarity(query_embedding, list(chunk.embedding))),
                keyword_score=0.0,
            )
            for chunk, source in embedded_chunks
        ]


def _terms(text: str) -> list[str]:
    terms = _latin_terms(text)
    for cjk_text in re.findall(r"[\u4e00-\u9fff]+", text.lower()):
        terms.extend(_cjk_ngrams(cjk_text))
    return terms


def _latin_terms(text: str) -> list[str]:
    return re.findall(r"[a-z0-9_]+", text.lower())


def _cjk_ngrams(text: str) -> list[str]:
    if len(text) <= 4:
        return [text]
    grams: list[str] = []
    for size in range(2, 5):
        grams.extend(text[index : index + size] for index in range(0, len(text) - size + 1))
    return grams


def _contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)
