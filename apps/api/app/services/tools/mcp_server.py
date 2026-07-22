"""MCP (Model Context Protocol) Tool Server.

Implements a minimal MCP-compatible tool server that exposes tool discovery
and tool calling endpoints, allowing external MCP clients to discover and
invoke registered tools.

Protocol reference: https://modelcontextprotocol.io
"""

from dataclasses import dataclass, field

from app.services.tools.registry import ToolRegistry
from app.services.tools.types import ToolCall


@dataclass
class MCPServerInfo:
    name: str = "FusionAgentStudio-MCP"
    version: str = "1.0.0"
    protocol_version: str = "2024-11-05"


@dataclass
class MCPToolDescriptor:
    """MCP-compatible tool description."""

    name: str
    description: str
    inputSchema: dict = field(default_factory=dict)


class MCPServer:
    """Minimal MCP server that wraps a ToolRegistry.

    Provides:
        - list_tools(): returns MCP-compatible tool descriptors
        - call_tool(name, arguments): executes a tool and returns MCP-compatible result
    """

    def __init__(self, registry: ToolRegistry, server_info: MCPServerInfo | None = None):
        self.registry = registry
        self.info = server_info or MCPServerInfo()

    def list_tools(self) -> list[MCPToolDescriptor]:
        """Return all registered tools as MCP-compatible descriptors."""
        descriptors: list[MCPToolDescriptor] = []
        for tool_def in self.registry.list_definitions():
            schema = tool_def.to_openai_schema()
            input_schema = schema.get("function", {}).get("parameters", {})
            descriptors.append(
                MCPToolDescriptor(
                    name=tool_def.name,
                    description=tool_def.description,
                    inputSchema=input_schema,
                )
            )
        return descriptors

    async def call_tool(self, name: str, arguments: dict | None = None) -> dict:
        """Execute a tool by name and return an MCP-compatible result."""
        tool_call = ToolCall(
            id="mcp-call",
            name=name,
            arguments=arguments or {},
        )
        result = await self.registry.execute(tool_call)
        return {
            "content": [
                {
                    "type": "text",
                    "text": result.content,
                }
            ],
            "isError": False,
        }

    def get_server_info(self) -> dict:
        return {
            "name": self.info.name,
            "version": self.info.version,
            "protocolVersion": self.info.protocol_version,
        }
