import hashlib
from dataclasses import dataclass, field
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import KnowledgeChunk, KnowledgeSource
from app.db.session import SessionLocal
from app.services.ingestion.chunking import chunk_text
from app.services.ingestion.cleaning import clean_text
from app.services.ingestion.parsers import parse_docx, parse_markdown, parse_pdf, parse_text, parse_web_url
from app.services.model_gateway.factory import get_model_gateway
from app.services.model_gateway.types import ModelGateway


@dataclass(frozen=True)
class IndexedChunkDraft:
    source_id: UUID
    knowledge_base_id: UUID
    chunk_index: int
    content: str
    content_hash: str
    token_count: int
    embedding: list[float] | None
    metadata: dict = field(default_factory=dict)


def build_indexed_chunks(
    source_id: UUID,
    knowledge_base_id: UUID,
    raw_text: str,
    gateway: ModelGateway,
    max_chars: int = 1200,
    overlap_chars: int = 160,
) -> list[IndexedChunkDraft]:
    text_chunks = chunk_text(clean_text(raw_text), max_chars=max_chars, overlap_chars=overlap_chars)
    if not text_chunks:
        return []

    embeddings = gateway.embed_texts([chunk.content for chunk in text_chunks])
    return [
        IndexedChunkDraft(
            source_id=source_id,
            knowledge_base_id=knowledge_base_id,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            content_hash=_content_hash(chunk.content),
            token_count=chunk.token_count,
            embedding=embeddings[index] if index < len(embeddings) else None,
            metadata={"source": "ingestion"},
        )
        for index, chunk in enumerate(text_chunks)
    ]


def ingest_source(source_id: str, db: Session | None = None, gateway: ModelGateway | None = None) -> None:
    owns_session = db is None
    session = db or SessionLocal()
    source_uuid = UUID(source_id)

    try:
        source = session.get(KnowledgeSource, source_uuid)
        if source is None:
            raise ValueError("Source not found")

        source.status = "indexing"
        source.error_message = ""
        session.flush()

        raw_text = load_source_text(source)
        drafts = build_indexed_chunks(
            source_id=source.id,
            knowledge_base_id=source.knowledge_base_id,
            raw_text=raw_text,
            gateway=gateway or get_model_gateway(),
        )

        session.query(KnowledgeChunk).filter(KnowledgeChunk.source_id == source.id).delete()
        session.add_all(
            KnowledgeChunk(
                source_id=draft.source_id,
                knowledge_base_id=draft.knowledge_base_id,
                chunk_index=draft.chunk_index,
                content=draft.content,
                content_hash=draft.content_hash,
                token_count=draft.token_count,
                chunk_metadata=draft.metadata,
                embedding=draft.embedding,
            )
            for draft in drafts
        )

        source.status = "indexed"
        session.commit()
    except Exception as exc:
        session.rollback()
        source = session.get(KnowledgeSource, source_uuid)
        if source is not None:
            source.status = "failed"
            source.error_message = str(exc)
            session.commit()
        raise
    finally:
        if owns_session:
            session.close()


def _content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def load_source_text(source: KnowledgeSource) -> str:
    if source.source_type == "note":
        return str(source.source_metadata.get("content", ""))
    if source.source_type == "web":
        return parse_web_url(source.uri)
    if source.storage_path:
        return _load_file_text(source)
    raise ValueError(f"Unsupported source type: {source.source_type}")


def _load_file_text(source: KnowledgeSource) -> str:
    from pathlib import Path

    path = Path(source.storage_path)
    if source.source_type == "pdf" or path.suffix.lower() == ".pdf":
        return parse_pdf(path)
    if source.source_type == "docx" or path.suffix.lower() == ".docx":
        return parse_docx(path)
    if source.source_type == "markdown" or path.suffix.lower() in {".md", ".markdown"}:
        return parse_markdown(path)
    if source.source_type == "txt" or path.suffix.lower() in {".txt", ".text"}:
        return parse_text(path)
    raise ValueError(f"Unsupported file source type: {source.source_type}")
