from dataclasses import dataclass, field


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str | None = None
    tool_calls: list[dict] | None = None
    tool_call_id: str | None = None
    name: str | None = None


@dataclass(frozen=True)
class ChatResult:
    content: str | None = None
    tool_calls: list[dict] = field(default_factory=list)
    usage: dict = field(default_factory=dict)


@dataclass(frozen=True)
class ToolChatResult:
    """Extended result that may carry a tool call instead of text content."""

    content: str | None = None
    tool_calls: list[dict] = field(default_factory=list)
    usage: dict = field(default_factory=dict)
    finish_reason: str = "stop"


class ModelGateway:
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

    def chat(self, messages: list[ChatMessage], model: str, temperature: float) -> ChatResult:
        raise NotImplementedError

    def chat_with_tools(
        self,
        messages: list[ChatMessage],
        model: str,
        temperature: float,
        tools: list[dict],
    ) -> ToolChatResult:
        """Chat with Function Calling support. Returns ToolChatResult which may
        contain tool_calls instead of plain text content."""
        raise NotImplementedError
