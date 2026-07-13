from uuid import uuid4

from app.services.retrieval.hybrid import merge_retrieval_candidates
from app.services.retrieval.types import RetrievalCandidate


def make_candidate(chunk_id, vector_score, keyword_score):
    return RetrievalCandidate(
        chunk_id=chunk_id,
        source_id=uuid4(),
        knowledge_base_id=uuid4(),
        content="content",
        source_title="source",
        chunk_index=0,
        vector_score=vector_score,
        keyword_score=keyword_score,
    )


def test_merge_retrieval_candidates_deduplicates_and_sorts():
    shared_id = uuid4()
    candidates = [
        make_candidate(shared_id, 0.8, 0.1),
        make_candidate(shared_id, 0.7, 0.9),
        make_candidate(uuid4(), 0.2, 0.1),
    ]

    results = merge_retrieval_candidates(candidates, limit=2)

    assert len(results) == 2
    assert results[0].chunk_id == shared_id
    assert results[0].score > results[1].score
