from uuid import uuid4

from app.services.agent_runtime.citations import build_citations
from app.services.retrieval.types import RetrievalResult


def test_build_citations_maps_retrieval_results():
    result = RetrievalResult(
        chunk_id=uuid4(),
        source_id=uuid4(),
        source_title="Guide",
        chunk_index=2,
        content="A useful excerpt for the user.",
        score=0.88,
    )

    citations = build_citations([result])

    assert citations[0]["title"] == "Guide"
    assert citations[0]["chunk_index"] == 2
    assert citations[0]["excerpt"] == "A useful excerpt for the user."
