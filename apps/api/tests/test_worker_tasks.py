def test_ingest_source_task_calls_indexer(monkeypatch):
    calls = []

    def fake_ingest_source(source_id: str):
        calls.append(source_id)

    monkeypatch.setattr("app.services.ingestion.indexer.ingest_source", fake_ingest_source)

    from app.workers.tasks import ingest_source_task

    result = ingest_source_task.run("source-1")

    assert calls == ["source-1"]
    assert result == {"source_id": "source-1", "status": "indexed"}
