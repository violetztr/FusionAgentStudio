from uuid import uuid4

from app.db.models import KnowledgeSource
from app.services.ingestion.indexer import build_indexed_chunks, load_source_text
from app.services.model_gateway.types import ChatMessage, ChatResult, ModelGateway


class FakeGateway(ModelGateway):
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[float(index), 0.0, 1.0] for index, _ in enumerate(texts)]

    def chat(self, messages: list[ChatMessage], model: str, temperature: float) -> ChatResult:
        return ChatResult(content="", usage={})


def test_build_indexed_chunks_cleans_chunks_and_embeds_text():
    source_id = uuid4()
    knowledge_base_id = uuid4()

    chunks = build_indexed_chunks(
        source_id=source_id,
        knowledge_base_id=knowledge_base_id,
        raw_text="Title\n\n\nalpha " * 60,
        gateway=FakeGateway(),
        max_chars=180,
        overlap_chars=30,
    )

    assert len(chunks) > 1
    assert chunks[0].source_id == source_id
    assert chunks[0].knowledge_base_id == knowledge_base_id
    assert chunks[0].chunk_index == 0
    assert chunks[0].embedding == [0.0, 0.0, 1.0]
    assert "\n\n\n" not in chunks[0].content
    assert chunks[0].content_hash


def test_load_source_text_reads_text_storage_path(tmp_path):
    path = tmp_path / "handbook.txt"
    path.write_text("Refund policy from a file", encoding="utf-8")
    source = KnowledgeSource(source_type="txt", storage_path=str(path), source_metadata={})

    assert load_source_text(source) == "Refund policy from a file"
