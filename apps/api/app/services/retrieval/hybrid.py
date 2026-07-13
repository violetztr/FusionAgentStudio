from app.services.retrieval.types import RetrievalCandidate, RetrievalResult


def merge_retrieval_candidates(candidates: list[RetrievalCandidate], limit: int) -> list[RetrievalResult]:
    best_by_chunk: dict[str, RetrievalCandidate] = {}
    best_score_by_chunk: dict[str, float] = {}

    for candidate in candidates:
        score = candidate.vector_score * 0.7 + candidate.keyword_score * 0.3
        key = str(candidate.chunk_id)
        if key not in best_score_by_chunk or score > best_score_by_chunk[key]:
            best_score_by_chunk[key] = score
            best_by_chunk[key] = candidate

    sorted_items = sorted(
        best_by_chunk.values(),
        key=lambda item: best_score_by_chunk[str(item.chunk_id)],
        reverse=True,
    )

    return [
        RetrievalResult(
            chunk_id=item.chunk_id,
            source_id=item.source_id,
            source_title=item.source_title,
            chunk_index=item.chunk_index,
            content=item.content,
            score=best_score_by_chunk[str(item.chunk_id)],
        )
        for item in sorted_items[:limit]
    ]
