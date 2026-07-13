from dataclasses import dataclass

from app.services.agent_runtime.citations import build_citations
from app.services.agent_runtime.prompt_builder import build_messages
from app.services.model_gateway.types import ModelGateway
from app.services.retrieval.types import RetrievalResult


@dataclass(frozen=True)
class AgentRuntimeResult:
    answer: str
    citations: list[dict]
    usage: dict


def run_agent_answer(
    gateway: ModelGateway,
    agent_prompt: str,
    question: str,
    model_name: str,
    temperature: float,
    citation_required: bool,
    retrieval_results: list[RetrievalResult],
) -> AgentRuntimeResult:
    if citation_required and not retrieval_results:
        return AgentRuntimeResult(
            answer="The knowledge base does not contain enough information to answer this question.",
            citations=[],
            usage={},
        )

    messages = build_messages(
        agent_prompt=agent_prompt,
        question=question,
        retrieval_results=retrieval_results,
        citation_required=citation_required,
    )
    chat_result = gateway.chat(messages=messages, model=model_name, temperature=temperature)
    return AgentRuntimeResult(
        answer=chat_result.content,
        citations=build_citations(retrieval_results),
        usage=chat_result.usage,
    )
