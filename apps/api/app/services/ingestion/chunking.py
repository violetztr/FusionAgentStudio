from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    chunk_index: int
    content: str
    token_count: int


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def chunk_text(text: str, max_chars: int = 1200, overlap_chars: int = 160) -> list[TextChunk]:
    normalized = text.strip()
    if not normalized:
        return []

    chunks: list[TextChunk] = []
    start = 0
    index = 0
    while start < len(normalized):
        end = min(start + max_chars, len(normalized))
        content = normalized[start:end].strip()
        if content:
            chunks.append(TextChunk(chunk_index=index, content=content, token_count=estimate_tokens(content)))
            index += 1
        if end == len(normalized):
            break
        start = max(0, end - overlap_chars)
    return chunks
