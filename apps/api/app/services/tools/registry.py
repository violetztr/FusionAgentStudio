import json
from typing import Any

from app.services.tools.types import ToolCall, ToolDefinition, ToolResult


class ToolRegistry:
    """Central registry for tool discovery, validation, and execution."""

    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        """Register a tool definition.

        Raises ValueError if a tool with the same name is already registered.
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered.")
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> None:
        self._tools.pop(name, None)

    def list_definitions(self) -> list[ToolDefinition]:
        return list(self._tools.values())

    def get_schemas(self) -> list[dict]:
        """Return OpenAI-compatible JSON Schema definitions for all registered tools."""
        return [tool.to_openai_schema() for tool in self._tools.values()]

    async def execute(self, tool_call: ToolCall) -> ToolResult:
        """Validate parameters and execute the tool call.

        Raises ValueError if the tool is unknown.
        """
        tool = self._tools.get(tool_call.name)
        if tool is None:
            raise ValueError(f"Unknown tool: {tool_call.name}")

        validated = self._validate_and_fill_defaults(tool, tool_call.arguments)
        result_content = await tool.handler(**validated)
        return ToolResult(
            tool_call_id=tool_call.id,
            name=tool_call.name,
            content=str(result_content),
        )

    def _validate_and_fill_defaults(self, tool: ToolDefinition, arguments: dict) -> dict:
        """Validate arguments against JSON Schema and fill in defaults."""
        filled: dict[str, Any] = {}
        for param in tool.parameters:
            value = arguments.get(param.name)
            if value is None:
                if param.required:
                    raise ValueError(
                        f"Missing required parameter '{param.name}' for tool '{tool.name}'"
                    )
                value = param.default
            else:
                if param.type == "string" and not isinstance(value, str):
                    raise ValueError(
                        f"Parameter '{param.name}' expected string, got {type(value).__name__}"
                    )
                if param.type in ("number", "integer") and not isinstance(value, (int, float)):
                    raise ValueError(
                        f"Parameter '{param.name}' expected number, got {type(value).__name__}"
                    )
                if param.type == "boolean" and not isinstance(value, bool):
                    raise ValueError(
                        f"Parameter '{param.name}' expected boolean, got {type(value).__name__}"
                    )
                if param.enum and value not in param.enum:
                    raise ValueError(
                        f"Parameter '{param.name}' must be one of {param.enum}, got '{value}'"
                    )
            filled[param.name] = value
        return filled


def parse_tool_calls(raw_response: dict) -> list[ToolCall]:
    """Parse tool calls from an OpenAI chat-completion response chunk or object."""
    tool_calls: list[ToolCall] = []
    choices = raw_response.get("choices", [])
    for choice in choices:
        message = choice.get("message") or {}
        for tc in message.get("tool_calls", []):
            func = tc.get("function", {})
            args = {}
            try:
                args = json.loads(func.get("arguments", "{}"))
            except json.JSONDecodeError:
                args = {}
            tool_calls.append(
                ToolCall(
                    id=tc.get("id", ""),
                    name=func.get("name", ""),
                    arguments=args,
                )
            )
    return tool_calls
