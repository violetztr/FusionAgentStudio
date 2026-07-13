from app.services.retrieval.types import RetrievalResult


def build_citations(results: list[RetrievalResult]) -> list[dict]:
    return [
        {
            "source_id": str(result.source_id),
            "chunk_id": str(result.chunk_id),
            "title": result.source_title,
            "chunk_index": result.chunk_index,
            "score": result.score,
            "excerpt": result.content[:360],
        }
        for result in results
    ]
