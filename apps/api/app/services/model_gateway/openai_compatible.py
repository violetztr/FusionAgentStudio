from openai import OpenAI

from app.core.config import settings
from app.services.model_gateway.types import ChatMessage, ChatResult, ModelGateway


class OpenAICompatibleGateway(ModelGateway):
    def __init__(self):
        self.client = OpenAI(api_key=settings.model_api_key, base_url=settings.model_base_url)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=settings.embedding_model, input=texts)
        return [item.embedding for item in response.data]

    def chat(self, messages: list[ChatMessage], model: str, temperature: float) -> ChatResult:
        response = self.client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[{"role": item.role, "content": item.content} for item in messages],
        )
        content = response.choices[0].message.content or ""
        usage = response.usage.model_dump() if response.usage else {}
        return ChatResult(content=content, usage=usage)
