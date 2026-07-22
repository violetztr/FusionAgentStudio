"""ReAct (Reasoning + Acting) Agent loop.

Implements the iterative Thought → Action → Observation cycle with
Function Calling, bounded iterations, and streaming event emission.
"""

import json
from dataclasses import dataclass, field
from typing import AsyncIterator

from app.services.model_gateway.types import (
    ChatMessage,
    ModelGateway,
    ToolChatResult,
)
from app.services.tools.registry import ToolRegistry


MAX_ITERATIONS = 10

SYSTEM_PROMPT = """You are a ReAct (Reasoning + Acting) Agent.
Follow this cycle for every user request:

1. **Thought**: Analyze the request. Decide if you need to use a tool or can answer directly.
2. **Action**: If a tool is needed, call the appropriate function with correct parameters.
   If no tool is needed, proceed directly to the final answer.
3. **Observation**: After receiving a tool result, evaluate it.
   - If it answers the request, proceed to the final answer.
   - If more information is needed, return to step 1 and call another tool.
4. **Final Answer**: Provide a clear, complete answer based on observations gathered.

Rules:
- Use tools when you need real-time data, calculations, or knowledge-base search.
- Do NOT call the same tool repeatedly with the same parameters.
- When the knowledge base returns insufficient results, tell the user honestly.
- Cite the source when using knowledge base results.
- Always end with a direct answer to the user's question."""


@dataclass
class ReActStep:
    step_type: str  # "thought" | "action" | "observation" | "final_answer"
    content: str
    tool_name: str | None = None
    tool_input: dict | None = None
    tool_result: str | None = None


@dataclass
class ReActResult:
    final_answer: str
    steps: list[ReActStep] = field(default_factory=list)
    total_tool_calls: int = 0
    total_iterations: int = 0
    usage: dict = field(default_factory=dict)


async def run_react_loop(
    gateway: ModelGateway,
    registry: ToolRegistry,
    user_message: str,
    model: str,
    temperature: float,
    system_prompt: str = "",
) -> ReActResult:
    """Execute the ReAct agent loop.

    Yields progress events as ReActStep objects, culminating in
    a final ReActResult containing the complete answer and trace.
    """
    tools = registry.get_schemas()
    effective_system = system_prompt or SYSTEM_PROMPT

    messages: list[ChatMessage] = [
        ChatMessage(role="system", content=effective_system),
        ChatMessage(role="user", content=user_message),
    ]

    steps: list[ReActStep] = []
    total_tool_calls = 0
    accumulated_usage: dict = {}

    for iteration in range(1, MAX_ITERATIONS + 1):
        result = gateway.chat_with_tools(
            messages=messages,
            model=model,
            temperature=temperature,
            tools=tools,
        )

        if result.usage:
            accumulated_usage = result.usage

        if result.tool_calls:
            # ---- ACTION ----
            assistant_msg: dict = {"role": "assistant", "content": result.content, "tool_calls": result.tool_calls}
            messages.append(_dict_to_chat_message(assistant_msg))

            for tc in result.tool_calls:
                func = tc.get("function", {})
                tool_name = func.get("name", "")
                tool_args = {}
                try:
                    tool_args = json.loads(func.get("arguments", "{}"))
                except json.JSONDecodeError:
                    tool_args = {}

                step = ReActStep(
                    step_type="action",
                    content=f"Calling tool: {tool_name}",
                    tool_name=tool_name,
                    tool_input=tool_args,
                )
                steps.append(step)

                # ---- OBSERVATION ----
                try:
                    from app.services.tools.registry import ToolCall
                    tool_call = ToolCall(id=tc.get("id", ""), name=tool_name, arguments=tool_args)
                    tool_result = await registry.execute(tool_call)
                    obs_content = tool_result.content
                except Exception as exc:
                    obs_content = f"Error executing tool '{tool_name}': {exc}"

                obs_step = ReActStep(
                    step_type="observation",
                    content=obs_content,
                    tool_name=tool_name,
                    tool_result=obs_content,
                )
                steps.append(obs_step)

                messages.append(ChatMessage(
                    role="tool",
                    content=obs_content,
                    tool_call_id=tc.get("id", ""),
                ))

                total_tool_calls += 1
        else:
            # ---- FINAL ANSWER ----
            final_content = result.content or ""
            steps.append(ReActStep(
                step_type="final_answer",
                content=final_content,
            ))
            messages.append(ChatMessage(role="assistant", content=final_content))

            return ReActResult(
                final_answer=final_content,
                steps=steps,
                total_tool_calls=total_tool_calls,
                total_iterations=iteration,
                usage=accumulated_usage,
            )

    # Max iterations reached without a final answer
    return ReActResult(
        final_answer="The agent reached the maximum allowed iterations without producing a final answer. Please try again with a more specific question.",
        steps=steps,
        total_tool_calls=total_tool_calls,
        total_iterations=MAX_ITERATIONS,
        usage=accumulated_usage,
    )


def _dict_to_chat_message(msg: dict) -> ChatMessage:
    return ChatMessage(
        role=msg.get("role", ""),
        content=msg.get("content"),
        tool_calls=msg.get("tool_calls"),
        tool_call_id=msg.get("tool_call_id"),
        name=msg.get("name"),
    )
