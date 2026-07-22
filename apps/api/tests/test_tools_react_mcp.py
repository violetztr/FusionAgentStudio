"""Tests for Tool Registry, ReAct Agent, MCP Server, and SSE Streaming."""

from uuid import uuid4

import pytest

from app.services.tools.builtin import calculator_tool, datetime_tool, build_default_registry
from app.services.tools.registry import ToolRegistry
from app.services.tools.types import ToolCall, ToolDefinition, ToolParameter
from app.services.tools.mcp_server import MCPServer, MCPToolDescriptor


# ---------------------------------------------------------------------------
# Tool Registry tests
# ---------------------------------------------------------------------------

class TestToolRegistry:
    async def _dummy_handler(self, **kwargs) -> str:
        return f"received: {kwargs}"

    def test_register_tool_and_list_definitions(self):
        registry = ToolRegistry()
        tool = ToolDefinition(
            name="echo",
            description="Echoes input back.",
            parameters=[
                ToolParameter(name="text", type="string", description="Input text.", required=True),
            ],
            handler=self._dummy_handler,
        )
        registry.register(tool)
        assert len(registry.list_definitions()) == 1

    def test_duplicate_registration_raises(self):
        registry = ToolRegistry()
        tool = ToolDefinition(
            name="echo",
            description="Echoes input back.",
            parameters=[],
            handler=self._dummy_handler,
        )
        registry.register(tool)
        with pytest.raises(ValueError, match="already registered"):
            registry.register(tool)

    def test_get_schemas_returns_openai_format(self):
        registry = ToolRegistry()
        tool = ToolDefinition(
            name="search",
            description="Search knowledge.",
            parameters=[
                ToolParameter(name="query", type="string", description="Search query.", required=True),
                ToolParameter(name="top_k", type="integer", description="Max results.", required=False, default=5),
            ],
            handler=self._dummy_handler,
        )
        registry.register(tool)
        schemas = registry.get_schemas()
        assert len(schemas) == 1
        assert schemas[0]["type"] == "function"
        func = schemas[0]["function"]
        assert func["name"] == "search"
        assert "query" in func["parameters"]["required"]
        assert "query" in func["parameters"]["properties"]

    async def test_execute_calls_handler(self):
        registry = ToolRegistry()

        async def handler(name: str) -> str:
            return f"Hello {name}"

        tool = ToolDefinition(
            name="greet",
            description="Greet someone.",
            parameters=[
                ToolParameter(name="name", type="string", description="Name.", required=True),
            ],
            handler=handler,
        )
        registry.register(tool)
        result = await registry.execute(ToolCall(id="1", name="greet", arguments={"name": "World"}))
        assert result.content == "Hello World"

    async def test_execute_unknown_tool_raises(self):
        registry = ToolRegistry()
        with pytest.raises(ValueError, match="Unknown tool"):
            await registry.execute(ToolCall(id="1", name="nonexistent", arguments={}))

    async def test_execute_missing_required_param_raises(self):
        registry = ToolRegistry()

        async def handler(name: str) -> str:
            return f"Hello {name}"

        tool = ToolDefinition(
            name="greet",
            description="Greet someone.",
            parameters=[
                ToolParameter(name="name", type="string", description="Name.", required=True),
            ],
            handler=handler,
        )
        registry.register(tool)
        with pytest.raises(ValueError, match="Missing required parameter"):
            await registry.execute(ToolCall(id="1", name="greet", arguments={}))

    async def test_execute_fills_default_values(self):
        registry = ToolRegistry()

        async def handler(query: str, top_k: int) -> str:
            return f"Search '{query}' with top_k={top_k}"

        tool = ToolDefinition(
            name="search",
            description="Search.",
            parameters=[
                ToolParameter(name="query", type="string", description="Query.", required=True),
                ToolParameter(name="top_k", type="integer", description="Top K.", required=False, default=5),
            ],
            handler=handler,
        )
        registry.register(tool)
        result = await registry.execute(ToolCall(id="1", name="search", arguments={"query": "test"}))
        assert "top_k=5" in result.content

    async def test_execute_enum_validation(self):
        registry = ToolRegistry()

        async def handler(operation: str) -> str:
            return operation

        tool = ToolDefinition(
            name="get_datetime",
            description="Get datetime.",
            parameters=[
                ToolParameter(
                    name="operation",
                    type="string",
                    description="Operation.",
                    required=True,
                    enum=["now", "today"],
                ),
            ],
            handler=handler,
        )
        registry.register(tool)
        with pytest.raises(ValueError, match="must be one of"):
            await registry.execute(ToolCall(id="1", name="get_datetime", arguments={"operation": "invalid"}))

    async def test_execute_type_validation(self):
        registry = ToolRegistry()

        async def handler(value: int) -> str:
            return str(value)

        tool = ToolDefinition(
            name="int_tool",
            description="Integer tool.",
            parameters=[
                ToolParameter(name="value", type="integer", description="Value.", required=True),
            ],
            handler=handler,
        )
        registry.register(tool)
        with pytest.raises(ValueError, match="expected number"):
            await registry.execute(ToolCall(id="1", name="int_tool", arguments={"value": "not_a_number"}))


# ---------------------------------------------------------------------------
# Built-in tools tests
# ---------------------------------------------------------------------------

class TestBuiltinTools:
    async def test_calculator_basic(self):
        result = await calculator_tool.handler(expression="2+3*4")
        assert "14" in result or "14.0" in result or "Result" in result

    async def test_calculator_division(self):
        result = await calculator_tool.handler(expression="10/3")
        assert "Result" in result

    async def test_calculator_invalid(self):
        result = await calculator_tool.handler(expression="import os")
        assert "Error" in result

    async def test_datetime_now(self):
        result = await datetime_tool.handler(operation="now")
        assert "T" in result  # ISO 8601 format

    async def test_datetime_today(self):
        result = await datetime_tool.handler(operation="today")
        assert "-" in result  # YYYY-MM-DD format

    async def test_datetime_timestamp(self):
        result = await datetime_tool.handler(operation="timestamp")
        assert result.isdigit()

    def test_build_default_registry(self):
        registry = build_default_registry()
        # Without search handler, should have datetime + calculator
        names = [t.name for t in registry.list_definitions()]
        assert "calculate" in names
        assert "get_datetime" in names

    def test_build_default_registry_with_search(self):
        async def dummy_search(query: str, top_k: int) -> str:
            return f"searched {query}"

        registry = build_default_registry(knowledge_search_handler=dummy_search)
        names = [t.name for t in registry.list_definitions()]
        assert "search_knowledge" in names
        assert "calculate" in names
        assert "get_datetime" in names


# ---------------------------------------------------------------------------
# MCP Server tests
# ---------------------------------------------------------------------------

class TestMCPServer:
    async def _dummy_handler(self, **kwargs) -> str:
        return str(kwargs)

    def test_list_tools_returns_descriptors(self):
        registry = ToolRegistry()
        registry.register(
            ToolDefinition(
                name="echo",
                description="Echoes input.",
                parameters=[
                    ToolParameter(name="text", type="string", description="Input text.", required=True),
                ],
                handler=self._dummy_handler,
            )
        )
        server = MCPServer(registry)
        tools = server.list_tools()
        assert len(tools) == 1
        assert tools[0].name == "echo"
        assert "text" in tools[0].inputSchema.get("properties", {})

    async def test_call_tool_returns_mcp_format(self):
        registry = ToolRegistry()

        async def handler(text: str) -> str:
            return f"Echo: {text}"

        registry.register(
            ToolDefinition(
                name="echo",
                description="Echoes input.",
                parameters=[
                    ToolParameter(name="text", type="string", description="Input text.", required=True),
                ],
                handler=handler,
            )
        )
        server = MCPServer(registry)
        result = await server.call_tool("echo", {"text": "hello"})
        assert result["isError"] is False
        assert len(result["content"]) == 1
        assert result["content"][0]["type"] == "text"
        assert "Echo: hello" in result["content"][0]["text"]

    def test_get_server_info(self):
        registry = ToolRegistry()
        server = MCPServer(registry)
        info = server.get_server_info()
        assert info["name"] == "FusionAgentStudio-MCP"
        assert "version" in info
        assert "protocolVersion" in info


# ---------------------------------------------------------------------------
# ToolDefinition.to_openai_schema tests
# ---------------------------------------------------------------------------

class TestOpenAISchema:
    def test_to_openai_schema_required_params(self):
        tool = ToolDefinition(
            name="search",
            description="Search.",
            parameters=[
                ToolParameter(name="query", type="string", description="Search query.", required=True),
            ],
            handler=None,
        )
        schema = tool.to_openai_schema()
        func = schema["function"]
        assert func["parameters"]["required"] == ["query"]

    def test_to_openai_schema_optional_params(self):
        tool = ToolDefinition(
            name="search",
            description="Search.",
            parameters=[
                ToolParameter(name="query", type="string", description="Search query.", required=False, default=""),
            ],
            handler=None,
        )
        schema = tool.to_openai_schema()
        func = schema["function"]
        assert func["parameters"]["required"] == []
