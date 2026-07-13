from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.runtime_log import RuntimeLogOut, RuntimeTraceOut
from app.services.logs.runtime_log_service import RuntimeLogService


router = APIRouter(tags=["runtime-logs"])


def get_runtime_log_service(db: Session = Depends(get_db)) -> RuntimeLogService:
    return RuntimeLogService(db)


@router.get("/api/runtime-logs", response_model=list[RuntimeLogOut])
def list_runtime_logs(service: RuntimeLogService = Depends(get_runtime_log_service)):
    return service.list()


@router.get("/api/conversations/{conversation_id}/traces", response_model=list[RuntimeTraceOut])
def list_conversation_traces(
    conversation_id: UUID,
    service: RuntimeLogService = Depends(get_runtime_log_service),
):
    return service.traces(conversation_id)
