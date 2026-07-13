from dataclasses import dataclass


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


@dataclass(frozen=True)
class ChatResult:
    content: str
    usage: dict


class ModelGateway:
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

    def chat(self, messages: list[ChatMessage], model: str, temperature: float) -> ChatResult:
        raise NotImplementedError
