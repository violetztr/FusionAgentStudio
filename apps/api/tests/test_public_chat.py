from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.routes.public_chat import get_public_chat_service


class FakePublicChatService:
    def __init__(self):
        self.published = {"published-agent": uuid4()}
        self.unpublished = {"draft-agent"}

    def get_public_agent(self, public_id: str):
        if public_id in self.published:
            return {
                "public_id": public_id,
                "name": "Published Agent",
                "description": "A published assistant",
            }
        return None

    def execute(self, public_id: str, message: str, conversation_id: UUID | None = None):
        if public_id not in self.published:
            return None
        return {
            "conversation_id": conversation_id or uuid4(),
            "answer": f"Answer to: {message}",
            "citations": [],
            "usage": {},
        }


def make_client():
    app.dependency_overrides.clear()
    service = FakePublicChatService()
    app.dependency_overrides[get_public_chat_service] = lambda: service
    return TestClient(app)


def test_unknown_public_agent_returns_404():
    client = make_client()

    response = client.post("/api/public/agents/missing-agent/chat", json={"message": "Hello"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Published agent not found"


def test_unpublished_agent_is_not_accessible():
    client = make_client()

    response = client.post("/api/public/agents/draft-agent/chat", json={"message": "Hello"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Published agent not found"


def test_published_agent_accepts_chat():
    client = make_client()

    response = client.post("/api/public/agents/published-agent/chat", json={"message": "Hello"})

    assert response.status_code == 200
    assert response.json()["answer"] == "Answer to: Hello"
