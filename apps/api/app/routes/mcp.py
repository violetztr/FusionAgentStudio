"""MCP (Model Context Protocol) API routes.

Exposes tool discovery and tool calling per agent, following MCP conventions.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models import Agent
from app.db.session import get_db
from app.services.tools.builtin import build_default_registry
from app.services.tools.mcp_server import MCPServer
from app.services.retrieval.service import RetrievalService

router = APIRouter(prefix="/api/mcp", tags=["mcp"])


@router.get("/agents/{agent_id}/server-info")
def mcp_server_info(agent_id: UUID, db: Session = Depends(get_db)):
    """Return MCP server metadata for a given agent."""
    agent = db.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    server = _build_mcp_server(agent, db)
    return server.get_server_info()


@router.get("/agents/{agent_id}/tools")
def mcp_list_tools(agent_id: UUID, db: Session = Depends(get_db)):
    """List available tools (MCP tool discovery) for a given agent."""
    agent = db.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    server = _build_mcp_server(agent, db)
    descriptors = server.list_tools()
    return {
        "tools": [
            {
                "name": d.name,
                "description": d.description,
                "inputSchema": d.inputSchema,
            }
            for d in descriptors
        ]
    }


@router.post("/agents/{agent_id}/tools/{tool_name}/call")
async def mcp_call_tool(
    agent_id: UUID,
    tool_name: str,
    arguments: dict | None = None,
    db: Session = Depends(get_db),
):
    """Execute a tool on behalf of an agent (MCP tool calling)."""
    agent = db.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    server = _build_mcp_server(agent, db)
    try:
        return await server.call_tool(tool_name, arguments)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _build_mcp_server(agent: Agent, db: Session) -> MCPServer:
    """Build an MCPServer preloaded with agent-bound tools."""
    retrieval_service = RetrievalService(db)

    async def bound_search(query: str, top_k: int) -> str:
        results = retrieval_service.retrieve_for_agent(agent.id, query, top_k)
        if not results:
            return "No relevant knowledge found in the bound knowledge bases."
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"[{i}] Source: {r.source_title} (chunk {r.chunk_index})\n{r.content}")
        return "\n\n".join(lines)

    registry = build_default_registry(knowledge_search_handler=bound_search)
    return MCPServer(registry)
