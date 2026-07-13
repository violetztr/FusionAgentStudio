from app.workers.celery_app import celery_app


@celery_app.task(name="ingest_source")
def ingest_source_task(source_id: str):
    from app.services.ingestion.indexer import ingest_source

    ingest_source(source_id)
    return {"source_id": source_id, "status": "indexed"}
