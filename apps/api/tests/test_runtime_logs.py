from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.routes.runtime_logs import get_runtime_log_service


class FakeRuntimeLogService:
    def __init__(self):
        self.conversation_id = uuid4()

    def list(self):
        return [
            {
                "conversation_id": self.conversation_id,
                "agent_name": "Support Agent",
                "channel": "debug",
                "message_count": 2,
                "last_question": "How long do refunds take?",
                "last_answer": "Refunds take seven days.",
                "citation_count": 1,
                "usage": {"total_tokens": 14},
            }
        ]

    def traces(self, conversation_id: UUID):
        if conversation_id != self.conversation_id:
            return []
        return [
            {
                "trace_type": "retrieval",
                "payload": {"chunks": 1},
            }
        ]


def make_client():
    app.dependency_overrides.clear()
    service = FakeRuntimeLogService()
    app.dependency_overrides[get_runtime_log_service] = lambda: service
    return TestClient(app), service


def test_runtime_logs_list_returns_latest_conversations():
    client, _ = make_client()

    response = client.get("/api/runtime-logs")

    assert response.status_code == 200
    body = response.json()
    assert body[0]["agent_name"] == "Support Agent"
    assert body[0]["citation_count"] == 1


def test_conversation_traces_returns_trace_payloads():
    client, service = make_client()

    response = client.get(f"/api/conversations/{service.conversation_id}/traces")

    assert response.status_code == 200
    assert response.json()[0]["trace_type"] == "retrieval"
