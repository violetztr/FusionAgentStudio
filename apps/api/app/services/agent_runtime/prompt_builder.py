from app.services.model_gateway.types import ChatMessage
from app.services.retrieval.types import RetrievalResult


BASE_POLICY = """You are a knowledge-grounded assistant configured by the platform.
Answer using only the supplied knowledge context when the question asks about bound knowledge.
If the context is insufficient, say that the knowledge base does not contain enough information.
Do not invent citations.
When citations are required, cite the exact source ids provided in the context.
Keep the answer direct, useful, and aligned with the agent's configured role."""


def build_context(results: list[RetrievalResult]) -> str:
    lines = []
    for index, result in enumerate(results, start=1):
        lines.append(
            f"[source:{index}] title={result.source_title} chunk_id={result.chunk_id} "
            f"source_id={result.source_id} chunk_index={result.chunk_index}\n{result.content}"
        )
    return "\n\n".join(lines)


def build_messages(
    agent_prompt: str,
    question: str,
    retrieval_results: list[RetrievalResult],
    citation_required: bool,
) -> list[ChatMessage]:
    citation_rule = "Citations are required." if citation_required else "Citations are optional."
    context = build_context(retrieval_results)
    system_content = f"{BASE_POLICY}\n\n{citation_rule}\n\nAgent instructions:\n{agent_prompt}\n\nKnowledge context:\n{context}"
    return [
        ChatMessage(role="system", content=system_content),
        ChatMessage(role="user", content=question),
    ]
