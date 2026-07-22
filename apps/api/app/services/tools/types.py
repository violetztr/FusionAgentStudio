from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine


@dataclass(frozen=True)
class ToolParameter:
    """JSON Schema parameter definition for a tool."""

    name: str
    type: str  # "string" | "number" | "integer" | "boolean" | "object" | "array"
    description: str
    required: bool = False
    enum: list[str] | None = None
    default: Any = None


@dataclass
class ToolDefinition:
    """Definition of a callable tool with JSON Schema validation."""

    name: str
    description: str
    parameters: list[ToolParameter]
    handler: Callable[..., Coroutine[Any, Any, str]]

    def to_openai_schema(self) -> dict:
        """Convert to OpenAI Function Calling JSON Schema format."""
        properties: dict[str, dict] = {}
        required: list[str] = []
        for param in self.parameters:
            prop: dict = {"type": param.type, "description": param.description}
            if param.enum:
                prop["enum"] = param.enum
            properties[param.name] = prop
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }


@dataclass
class ToolCall:
    """Represents a parsed tool call from the model."""

    id: str
    name: str
    arguments: dict = field(default_factory=dict)


@dataclass
class ToolResult:
    """Result returned by a tool execution."""

    tool_call_id: str
    name: str
    content: str
