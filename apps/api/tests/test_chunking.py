from app.services.ingestion.chunking import chunk_text


def test_chunk_text_preserves_order_and_overlap():
    text = "alpha " * 200

    chunks = chunk_text(text, max_chars=300, overlap_chars=50)

    assert len(chunks) > 1
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1
    assert chunks[0].content
    assert chunks[1].content
    assert chunks[0].content[-20:] in chunks[1].content
