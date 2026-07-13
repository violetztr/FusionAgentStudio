from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.routes.agents import get_agent_service


class FakeAgentService:
    def __init__(self):
        self.items = {}
        self.bindings = set()

    def list(self, workspace_id: UUID):
        return [item for item in self.items.values() if item["workspace_id"] == workspace_id]

    def create(self, workspace_id: UUID, payload):
        item = {
            "id": uuid4(),
            "workspace_id": workspace_id,
            "name": payload.name,
            "description": payload.description,
            "system_prompt": payload.system_prompt,
            "model_provider": payload.model_provider,
            "model_name": payload.model_name,
            "temperature": payload.temperature,
            "top_k": payload.top_k,
            "citation_required": payload.citation_required,
            "is_published": False,
            "public_id": "public-token",
        }
        self.items[item["id"]] = item
        return item

    def get(self, agent_id: UUID):
        return self.items.get(agent_id)

    def update(self, agent_id: UUID, payload):
        item = self.items.get(agent_id)
        if item is None:
            return None
        for field in ["name", "description", "system_prompt", "model_name", "temperature", "top_k", "citation_required"]:
            value = getattr(payload, field)
            if value is not None:
                item[field] = value
        return item

    def delete(self, agent_id: UUID):
        return self.items.pop(agent_id, None) is not None

    def bind_knowledge_base(self, agent_id: UUID, knowledge_base_id: UUID):
        if agent_id not in self.items:
            return False
        self.bindings.add((agent_id, knowledge_base_id))
        return True

    def unbind_knowledge_base(self, agent_id: UUID, knowledge_base_id: UUID):
        self.bindings.discard((agent_id, knowledge_base_id))
        return True

    def publish(self, agent_id: UUID):
        item = self.items.get(agent_id)
        if item is None:
            return None
        item["is_published"] = True
        return item

    def unpublish(self, agent_id: UUID):
        item = self.items.get(agent_id)
        if item is None:
            return None
        item["is_published"] = False
        return item


def make_client():
    app.dependency_overrides.clear()
    service = FakeAgentService()
    app.dependency_overrides[get_agent_service] = lambda: service
    return TestClient(app), service


def create_agent(client: TestClient, workspace_id: UUID):
    return client.post(
        f"/api/agents?workspace_id={workspace_id}",
        json={
            "name": "Product Assistant",
            "description": "Answers product questions",
            "system_prompt": "Answer from product knowledge.",
        },
    )


def test_create_agent():
    client, _ = make_client()
    workspace_id = uuid4()

    response = create_agent(client, workspace_id)

    assert response.status_code == 200
    body = response.json()
    assert body["workspace_id"] == str(workspace_id)
    assert body["name"] == "Product Assistant"
    assert body["model_provider"] == "openai_compatible"
    assert body["is_published"] is False


def test_bind_knowledge_base_to_agent():
    client, service = make_client()
    workspace_id = uuid4()
    agent_id = UUID(create_agent(client, workspace_id).json()["id"])
    knowledge_base_id = uuid4()

    response = client.post(
        f"/api/agents/{agent_id}/knowledge-bases",
        json={"knowledge_base_id": str(knowledge_base_id)},
    )

    assert response.status_code == 200
    assert response.json() == {"bound": True}
    assert (agent_id, knowledge_base_id) in service.bindings


def test_publish_agent_toggles_is_published():
    client, _ = make_client()
    workspace_id = uuid4()
    agent_id = create_agent(client, workspace_id).json()["id"]

    response = client.post(f"/api/agents/{agent_id}/publish")

    assert response.status_code == 200
    assert response.json()["is_published"] is True
