from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.routes.sources import get_source_service


class FakeSourceService:
    def __init__(self):
        self.sources = {}
        self.chunks = {}

    def create_web(self, knowledge_base_id: UUID, payload):
        source = self._source(knowledge_base_id, "web", payload.title, payload.url)
        self.sources[source["id"]] = source
        return source

    def create_note(self, knowledge_base_id: UUID, payload):
        source = self._source(knowledge_base_id, "note", payload.title, "")
        source["metadata"] = {"content": payload.content}
        self.sources[source["id"]] = source
        return source

    def list_by_knowledge_base(self, knowledge_base_id: UUID):
        return [item for item in self.sources.values() if item["knowledge_base_id"] == knowledge_base_id]

    def get_chunks(self, source_id: UUID):
        return self.chunks.get(source_id, [])

    def reindex(self, source_id: UUID):
        return source_id in self.sources

    def delete(self, source_id: UUID):
        return self.sources.pop(source_id, None) is not None

    def _source(self, knowledge_base_id: UUID, source_type: str, title: str, uri: str):
        return {
            "id": uuid4(),
            "knowledge_base_id": knowledge_base_id,
            "source_type": source_type,
            "title": title,
            "uri": uri,
            "storage_path": "",
            "status": "pending",
            "error_message": "",
            "metadata": {},
        }


def make_client():
    app.dependency_overrides.clear()
    service = FakeSourceService()
    app.dependency_overrides[get_source_service] = lambda: service
    return TestClient(app), service


def test_create_note_source():
    client, _ = make_client()
    knowledge_base_id = uuid4()

    response = client.post(
        f"/api/knowledge-bases/{knowledge_base_id}/sources/note",
        json={"title": "Release Notes", "content": "Version 1 ships retrieval."},
    )

    assert response.status_code == 200
    assert response.json()["source_type"] == "note"
    assert response.json()["metadata"]["content"] == "Version 1 ships retrieval."


def test_create_web_source():
    client, _ = make_client()
    knowledge_base_id = uuid4()

    response = client.post(
        f"/api/knowledge-bases/{knowledge_base_id}/sources/web",
        json={"title": "Docs", "url": "https://example.com/docs"},
    )

    assert response.status_code == 200
    assert response.json()["uri"] == "https://example.com/docs"


def test_list_sources_for_knowledge_base():
    client, _ = make_client()
    knowledge_base_id = uuid4()
    client.post(
        f"/api/knowledge-bases/{knowledge_base_id}/sources/note",
        json={"title": "Note", "content": "Knowledge"},
    )

    response = client.get(f"/api/knowledge-bases/{knowledge_base_id}/sources")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_delete_source():
    client, _ = make_client()
    knowledge_base_id = uuid4()
    created = client.post(
        f"/api/knowledge-bases/{knowledge_base_id}/sources/note",
        json={"title": "Temporary", "content": "Delete me"},
    ).json()

    response = client.delete(f"/api/sources/{created['id']}")

    assert response.status_code == 200
    assert response.json() == {"deleted": True}
