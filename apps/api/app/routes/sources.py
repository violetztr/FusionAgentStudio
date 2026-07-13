from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.source import NoteSourceCreate, SourceChunkOut, SourceOut, WebSourceCreate
from app.services.knowledge.source_service import SourceService


router = APIRouter(tags=["sources"])


def get_source_service(db: Session = Depends(get_db)) -> SourceService:
    return SourceService(db)


@router.post("/api/knowledge-bases/{knowledge_base_id}/sources/web", response_model=SourceOut)
def create_web_source(
    knowledge_base_id: UUID,
    payload: WebSourceCreate,
    service: SourceService = Depends(get_source_service),
):
    return service.create_web(knowledge_base_id, payload)


@router.post("/api/knowledge-bases/{knowledge_base_id}/sources/note", response_model=SourceOut)
def create_note_source(
    knowledge_base_id: UUID,
    payload: NoteSourceCreate,
    service: SourceService = Depends(get_source_service),
):
    return service.create_note(knowledge_base_id, payload)


@router.get("/api/knowledge-bases/{knowledge_base_id}/sources", response_model=list[SourceOut])
def list_sources(
    knowledge_base_id: UUID,
    service: SourceService = Depends(get_source_service),
):
    return service.list_by_knowledge_base(knowledge_base_id)


@router.get("/api/sources/{source_id}/chunks", response_model=list[SourceChunkOut])
def get_source_chunks(
    source_id: UUID,
    service: SourceService = Depends(get_source_service),
):
    return service.get_chunks(source_id)


@router.post("/api/sources/{source_id}/reindex")
def reindex_source(
    source_id: UUID,
    service: SourceService = Depends(get_source_service),
):
    indexed = service.reindex(source_id)
    if not indexed:
        raise HTTPException(status_code=404, detail="Source not found")
    return {"indexed": True}


@router.delete("/api/sources/{source_id}")
def delete_source(
    source_id: UUID,
    service: SourceService = Depends(get_source_service),
):
    deleted = service.delete(source_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Source not found")
    return {"deleted": True}
