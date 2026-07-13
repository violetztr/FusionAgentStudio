from app.services.model_gateway.types import ChatMessage, ChatResult, ModelGateway


class FakeGateway(ModelGateway):
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0, 0.0] for _ in texts]

    def chat(self, messages: list[ChatMessage], model: str, temperature: float) -> ChatResult:
        return ChatResult(content="answer", usage={"total_tokens": 3})


def test_fake_gateway_contract():
    gateway = FakeGateway()

    embeddings = gateway.embed_texts(["hello"])
    result = gateway.chat([ChatMessage(role="user", content="hi")], "test-model", 0.2)

    assert embeddings == [[1.0, 0.0, 0.0]]
    assert result.content == "answer"
    assert result.usage["total_tokens"] == 3
