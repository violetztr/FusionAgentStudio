from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import KnowledgeChunk, KnowledgeSource
from app.schemas.source import NoteSourceCreate, WebSourceCreate
from app.services.ingestion.indexer import ingest_source


class SourceService:
    def __init__(self, db: Session):
        self.db = db

    def create_web(self, knowledge_base_id: UUID, payload: WebSourceCreate) -> dict:
        source = KnowledgeSource(
            knowledge_base_id=knowledge_base_id,
            source_type="web",
            title=payload.title,
            uri=payload.url,
            storage_path="",
            status="pending",
            source_metadata={},
        )
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return serialize_source(source)

    def create_note(self, knowledge_base_id: UUID, payload: NoteSourceCreate) -> dict:
        source = KnowledgeSource(
            knowledge_base_id=knowledge_base_id,
            source_type="note",
            title=payload.title,
            uri="",
            storage_path="",
            status="pending",
            source_metadata={"content": payload.content},
        )
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return serialize_source(source)

    def list_by_knowledge_base(self, knowledge_base_id: UUID) -> list[dict]:
        sources = (
            self.db.query(KnowledgeSource)
            .filter(KnowledgeSource.knowledge_base_id == knowledge_base_id)
            .order_by(KnowledgeSource.created_at.desc())
            .all()
        )
        return [serialize_source(source) for source in sources]

    def get_chunks(self, source_id: UUID) -> list[dict]:
        chunks = (
            self.db.query(KnowledgeChunk)
            .filter(KnowledgeChunk.source_id == source_id)
            .order_by(KnowledgeChunk.chunk_index.asc())
            .all()
        )
        return [serialize_chunk(chunk) for chunk in chunks]

    def reindex(self, source_id: UUID) -> bool:
        if self.db.get(KnowledgeSource, source_id) is None:
            return False
        ingest_source(str(source_id), db=self.db)
        return True

    def delete(self, source_id: UUID) -> bool:
        source = self.db.get(KnowledgeSource, source_id)
        if source is None:
            return False
        self.db.query(KnowledgeChunk).filter(KnowledgeChunk.source_id == source_id).delete()
        self.db.delete(source)
        self.db.commit()
        return True


def serialize_source(source: KnowledgeSource) -> dict:
    return {
        "id": source.id,
        "knowledge_base_id": source.knowledge_base_id,
        "source_type": source.source_type,
        "title": source.title,
        "uri": source.uri,
        "storage_path": source.storage_path,
        "status": source.status,
        "error_message": source.error_message,
        "metadata": source.source_metadata,
    }


def serialize_chunk(chunk: KnowledgeChunk) -> dict:
    return {
        "id": chunk.id,
        "source_id": chunk.source_id,
        "knowledge_base_id": chunk.knowledge_base_id,
        "chunk_index": chunk.chunk_index,
        "content": chunk.content,
        "token_count": chunk.token_count,
        "metadata": chunk.chunk_metadata,
    }
