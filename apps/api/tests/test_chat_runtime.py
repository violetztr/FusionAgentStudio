from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.routes.chat import get_chat_service


class FakeChatService:
    def __init__(self, answer: str, citations: list[dict]):
        self.answer = answer
        self.citations = citations
        self.messages = []
        self.conversation_id = uuid4()

    def execute(self, agent_id: UUID, message: str, channel: str, conversation_id: UUID | None = None):
        self.messages.append({"role": "user", "content": message, "channel": channel})
        self.messages.append({"role": "assistant", "content": self.answer, "channel": channel})
        return {
            "conversation_id": conversation_id or self.conversation_id,
            "answer": self.answer,
            "citations": self.citations,
            "usage": {"total_tokens": 12} if self.citations else {},
        }


def make_client(service: FakeChatService):
    app.dependency_overrides.clear()
    app.dependency_overrides[get_chat_service] = lambda: service
    return TestClient(app)


def test_debug_chat_creates_conversation_and_returns_citations():
    citation = {
        "source_id": str(uuid4()),
        "chunk_id": str(uuid4()),
        "title": "Handbook",
        "chunk_index": 1,
        "score": 0.91,
        "excerpt": "Refunds are processed within seven days.",
    }
    service = FakeChatService("Refunds take seven days.", [citation])
    client = make_client(service)

    response = client.post(
        f"/api/agents/{uuid4()}/debug-chat",
        json={"message": "How long do refunds take?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Refunds take seven days."
    assert body["citations"] == [citation]
    assert len(service.messages) == 2
    assert service.messages[0]["channel"] == "debug"


def test_debug_chat_returns_insufficient_information_without_chunks():
    service = FakeChatService(
        "The knowledge base does not contain enough information to answer this question.",
        [],
    )
    client = make_client(service)

    response = client.post(
        f"/api/agents/{uuid4()}/debug-chat",
        json={"message": "What is the refund policy?"},
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "The knowledge base does not contain enough information to answer this question."
    assert response.json()["citations"] == []
