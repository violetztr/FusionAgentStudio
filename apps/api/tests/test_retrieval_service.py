from uuid import uuid4

from app.services.retrieval.service import build_keyword_candidate, keyword_score


def test_keyword_score_counts_case_insensitive_terms():
    score = keyword_score("Refund policy allows refunds", "What is the refund policy?")

    assert score > 0


def test_keyword_score_matches_cjk_substrings():
    score = keyword_score("退款政策允许七天内退款", "退款政策是什么")

    assert score > 0


def test_keyword_score_deduplicates_repeated_query_terms():
    score = keyword_score("refund", "refund refund refund")

    assert score == 1.0


def test_build_keyword_candidate_maps_chunk_and_source():
    chunk_id = uuid4()
    source_id = uuid4()
    knowledge_base_id = uuid4()

    candidate = build_keyword_candidate(
        chunk_id=chunk_id,
        source_id=source_id,
        knowledge_base_id=knowledge_base_id,
        content="Refund policy",
        source_title="Handbook",
        chunk_index=3,
        query="refund policy",
    )

    assert candidate.chunk_id == chunk_id
    assert candidate.source_title == "Handbook"
    assert candidate.keyword_score > 0
