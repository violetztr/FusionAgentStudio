from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.routes.knowledge_bases import get_knowledge_base_service


class FakeKnowledgeBaseService:
    def __init__(self):
        self.items = {}

    def list(self, workspace_id: UUID):
        return [item for item in self.items.values() if item["workspace_id"] == workspace_id]

    def create(self, workspace_id: UUID, payload):
        item = {
            "id": uuid4(),
            "workspace_id": workspace_id,
            "name": payload.name,
            "description": payload.description,
        }
        self.items[item["id"]] = item
        return item

    def get(self, knowledge_base_id: UUID):
        return self.items.get(knowledge_base_id)

    def update(self, knowledge_base_id: UUID, payload):
        item = self.items.get(knowledge_base_id)
        if item is None:
            return None
        if payload.name is not None:
            item["name"] = payload.name
        if payload.description is not None:
            item["description"] = payload.description
        return item

    def delete(self, knowledge_base_id: UUID):
        return self.items.pop(knowledge_base_id, None) is not None


def make_client():
    service = FakeKnowledgeBaseService()
    app.dependency_overrides[get_knowledge_base_service] = lambda: service
    return TestClient(app), service


def test_create_knowledge_base():
    client, _ = make_client()
    workspace_id = uuid4()

    response = client.post(
        f"/api/knowledge-bases?workspace_id={workspace_id}",
        json={"name": "Product Docs", "description": "External and internal product knowledge"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["workspace_id"] == str(workspace_id)
    assert body["name"] == "Product Docs"
    assert body["description"] == "External and internal product knowledge"


def test_list_knowledge_bases_filters_by_workspace():
    client, _ = make_client()
    workspace_id = uuid4()
    other_workspace_id = uuid4()
    client.post(f"/api/knowledge-bases?workspace_id={workspace_id}", json={"name": "Product Docs"})
    client.post(f"/api/knowledge-bases?workspace_id={other_workspace_id}", json={"name": "Other Docs"})

    response = client.get(f"/api/knowledge-bases?workspace_id={workspace_id}")

    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["name"] == "Product Docs"


def test_get_knowledge_base_by_id():
    client, _ = make_client()
    workspace_id = uuid4()
    created = client.post(f"/api/knowledge-bases?workspace_id={workspace_id}", json={"name": "Team Wiki"}).json()

    response = client.get(f"/api/knowledge-bases/{created['id']}")

    assert response.status_code == 200
    assert response.json()["name"] == "Team Wiki"


def test_update_knowledge_base():
    client, _ = make_client()
    workspace_id = uuid4()
    created = client.post(f"/api/knowledge-bases?workspace_id={workspace_id}", json={"name": "Old"}).json()

    response = client.patch(
        f"/api/knowledge-bases/{created['id']}",
        json={"name": "New", "description": "Updated description"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "New"
    assert response.json()["description"] == "Updated description"


def test_delete_knowledge_base():
    client, _ = make_client()
    workspace_id = uuid4()
    created = client.post(f"/api/knowledge-bases?workspace_id={workspace_id}", json={"name": "Temporary"}).json()

    delete_response = client.delete(f"/api/knowledge-bases/{created['id']}")
    get_response = client.get(f"/api/knowledge-bases/{created['id']}")

    assert delete_response.status_code == 200
    assert delete_response.json() == {"deleted": True}
    assert get_response.status_code == 404


def test_missing_knowledge_base_returns_404():
    client, _ = make_client()

    response = client.get(f"/api/knowledge-bases/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Knowledge base not found"
