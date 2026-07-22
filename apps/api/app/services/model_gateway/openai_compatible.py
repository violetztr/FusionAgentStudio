from openai import OpenAI

from app.core.config import settings
from app.services.model_gateway.types import ChatMessage, ChatResult, ModelGateway, ToolChatResult


class OpenAICompatibleGateway(ModelGateway):
    def __init__(self):
        self.client = OpenAI(api_key=settings.model_api_key, base_url=settings.model_base_url)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=settings.embedding_model, input=texts)
        return [item.embedding for item in response.data]

    def _build_messages(self, messages: list[ChatMessage]) -> list[dict]:
        """Convert internal ChatMessage list to OpenAI API format."""
        payload: list[dict] = []
        for msg in messages:
            item: dict = {"role": msg.role}
            if msg.content is not None:
                item["content"] = msg.content
            if msg.tool_calls:
                item["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                item["tool_call_id"] = msg.tool_call_id
            if msg.name:
                item["name"] = msg.name
            payload.append(item)
        return payload

    def chat(self, messages: list[ChatMessage], model: str, temperature: float) -> ChatResult:
        response = self.client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=self._build_messages(messages),
        )
        content = response.choices[0].message.content or ""
        usage = response.usage.model_dump() if response.usage else {}
        return ChatResult(content=content, usage=usage)

    def chat_with_tools(
        self,
        messages: list[ChatMessage],
        model: str,
        temperature: float,
        tools: list[dict],
    ) -> ToolChatResult:
        response = self.client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=self._build_messages(messages),
            tools=tools,
            tool_choice="auto",
        )
        choice = response.choices[0]
        finish_reason = choice.finish_reason or "stop"
        usage = response.usage.model_dump() if response.usage else {}

        raw_tool_calls = []
        if choice.message.tool_calls:
            raw_tool_calls = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in choice.message.tool_calls
            ]

        return ToolChatResult(
            content=choice.message.content,
            tool_calls=raw_tool_calls,
            usage=usage,
            finish_reason=finish_reason,
        )
