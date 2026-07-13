from app.services.agent_runtime.runtime import run_agent_answer
from app.services.model_gateway.types import ChatMessage, ChatResult, ModelGateway


class FakeGateway(ModelGateway):
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return []

    def chat(self, messages: list[ChatMessage], model: str, temperature: float) -> ChatResult:
        return ChatResult(content="grounded answer", usage={"total_tokens": 10})


def test_run_agent_answer_returns_insufficient_information_without_context():
    result = run_agent_answer(
        gateway=FakeGateway(),
        agent_prompt="Answer as support.",
        question="What is the refund policy?",
        model_name="test-model",
        temperature=0.2,
        citation_required=True,
        retrieval_results=[],
    )

    assert result.answer == "The knowledge base does not contain enough information to answer this question."
    assert result.citations == []
    assert result.usage == {}
