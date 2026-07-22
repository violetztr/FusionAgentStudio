"""Built-in tools: knowledge search, calculator, and datetime utilities."""

from datetime import datetime, timezone

from app.services.tools.types import ToolDefinition, ToolParameter


def create_knowledge_search_tool(handler) -> ToolDefinition:
    """Factory for the knowledge-base search tool.

    The handler must be an async callable that receives (query: str, top_k: int)
    and returns a formatted string of search results.
    """
    return ToolDefinition(
        name="search_knowledge",
        description="Search bound knowledge bases for relevant information. "
        "Use this when the user asks about domain-specific content that may be in the knowledge bases.",
        parameters=[
            ToolParameter(
                name="query",
                type="string",
                description="Natural-language search query to find relevant knowledge chunks.",
                required=True,
            ),
            ToolParameter(
                name="top_k",
                type="integer",
                description="Maximum number of knowledge chunks to retrieve (default 5).",
                required=False,
                default=5,
            ),
        ],
        handler=handler,
    )


async def _calculator_handler(expression: str) -> str:
    """Safely evaluate a mathematical expression."""
    # Only allow digits, operators, parentheses, spaces, and decimal points
    allowed = set("0123456789+-*/().%^ eE")
    sanitized = "".join(c for c in expression if c in allowed)
    if not sanitized:
        return "Error: expression contains no valid characters."
    try:
        result = eval(sanitized, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as exc:
        return f"Error evaluating expression: {exc}"


calculator_tool = ToolDefinition(
    name="calculate",
    description="Evaluate a mathematical expression. Supports +, -, *, /, **, %, and parentheses.",
    parameters=[
        ToolParameter(
            name="expression",
            type="string",
            description="Mathematical expression to evaluate (e.g., '2 + 3 * 4', 'sqrt(16)').",
            required=True,
        ),
    ],
    handler=_calculator_handler,
)


async def _datetime_handler(operation: str) -> str:
    now = datetime.now(timezone.utc)
    if operation == "now":
        return now.isoformat()
    if operation == "today":
        return now.strftime("%Y-%m-%d")
    if operation == "timestamp":
        return str(int(now.timestamp()))
    return f"Unsupported datetime operation: {operation}"


datetime_tool = ToolDefinition(
    name="get_datetime",
    description="Get current date, time, or timestamp.",
    parameters=[
        ToolParameter(
            name="operation",
            type="string",
            description="Operation to perform.",
            required=True,
            enum=["now", "today", "timestamp"],
        ),
    ],
    handler=_datetime_handler,
)


def build_default_registry(knowledge_search_handler=None):
    """Build a ToolRegistry preloaded with built-in tools.

    If `knowledge_search_handler` is provided, the knowledge search tool is
    also registered.
    """
    from app.services.tools.registry import ToolRegistry

    registry = ToolRegistry()
    registry.register(datetime_tool)
    registry.register(calculator_tool)
    if knowledge_search_handler:
        registry.register(create_knowledge_search_tool(knowledge_search_handler))
    return registry
