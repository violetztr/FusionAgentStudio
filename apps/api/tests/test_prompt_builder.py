from uuid import uuid4

from app.services.agent_runtime.prompt_builder import build_messages
from app.services.retrieval.types import RetrievalResult


def test_build_messages_includes_context_and_policy():
    chunk_id = uuid4()
    source_id = uuid4()
    results = [
        RetrievalResult(
            chunk_id=chunk_id,
            source_id=source_id,
            source_title="Handbook",
            chunk_index=1,
            content="Refunds are processed within seven days.",
            score=0.91,
        )
    ]

    messages = build_messages(
        agent_prompt="You are a support assistant.",
        question="How long do refunds take?",
        retrieval_results=results,
        citation_required=True,
    )

    assert messages[0].role == "system"
    assert "Do not invent citations" in messages[0].content
    assert "Refunds are processed" in messages[0].content
    assert messages[1].content == "How long do refunds take?"
