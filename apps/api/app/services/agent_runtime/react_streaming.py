"""Streaming version of the ReAct agent loop.

Emits SSE events for each React step (thought, action, observation, final_answer).
"""

import json
from typing import AsyncIterator

from app.services.agent_runtime.react_agent import (
    MAX_ITERATIONS,
    SYSTEM_PROMPT,
    ReActResult,
    ReActStep,
    _dict_to_chat_message,
)
from app.services.model_gateway.types import ChatMessage, ModelGateway
from app.services.tools.registry import ToolRegistry


async def run_react_loop_streaming(
    gateway: ModelGateway,
    registry: ToolRegistry,
    user_message: str,
    model: str,
    temperature: float,
    system_prompt: str = "",
) -> AsyncIterator[dict]:
    """Execute the ReAct agent loop, yielding SSE event dicts.

    Each yielded dict contains:
        event: str  -- "thought" | "action" | "observation" | "final_answer" | "error" | "done"
        data: dict  -- step payload or final result
    """
    tools = registry.get_schemas()
    effective_system = system_prompt or SYSTEM_PROMPT

    messages: list[ChatMessage] = [
        ChatMessage(role="system", content=effective_system),
        ChatMessage(role="user", content=user_message),
    ]

    total_tool_calls = 0
    accumulated_usage: dict = {}
    steps: list[ReActStep] = []

    yield {"event": "thought", "data": {"content": "Analyzing request and planning approach..."}}

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
            assistant_msg: dict = {
                "role": "assistant",
                "content": result.content,
                "tool_calls": result.tool_calls,
            }
            messages.append(_dict_to_chat_message(assistant_msg))

            for tc in result.tool_calls:
                func = tc.get("function", {})
                tool_name = func.get("name", "")
                tool_args = {}
                try:
                    tool_args = json.loads(func.get("arguments", "{}"))
                except json.JSONDecodeError:
                    tool_args = {}

                yield {
                    "event": "action",
                    "data": {
                        "tool_name": tool_name,
                        "tool_input": tool_args,
                        "iteration": iteration,
                    },
                }

                try:
                    from app.services.tools.registry import ToolCall

                    tool_call = ToolCall(id=tc.get("id", ""), name=tool_name, arguments=tool_args)
                    tool_result = await registry.execute(tool_call)
                    obs_content = tool_result.content
                except Exception as exc:
                    obs_content = f"Error executing tool '{tool_name}': {exc}"

                step = ReActStep(
                    step_type="observation",
                    content=obs_content,
                    tool_name=tool_name,
                    tool_result=obs_content,
                )
                steps.append(step)

                yield {
                    "event": "observation",
                    "data": {
                        "tool_name": tool_name,
                        "content": obs_content,
                    },
                }

                messages.append(
                    ChatMessage(
                        role="tool",
                        content=obs_content,
                        tool_call_id=tc.get("id", ""),
                    )
                )

                total_tool_calls += 1
        else:
            final_content = result.content or ""
            steps.append(ReActStep(step_type="final_answer", content=final_content))

            yield {
                "event": "final_answer",
                "data": {"content": final_content},
            }

            yield {
                "event": "done",
                "data": {
                    "final_answer": final_content,
                    "total_tool_calls": total_tool_calls,
                    "total_iterations": iteration,
                    "usage": accumulated_usage,
                    "steps": [
                        {
                            "step_type": s.step_type,
                            "content": s.content,
                            "tool_name": s.tool_name,
                            "tool_input": s.tool_input,
                            "tool_result": s.tool_result,
                        }
                        for s in steps
                    ],
                },
            }
            return

    yield {
        "event": "error",
        "data": {"content": "Maximum iterations reached without a final answer."},
    }
    yield {
        "event": "done",
        "data": {
            "final_answer": "Agent reached maximum iterations.",
            "total_tool_calls": total_tool_calls,
            "total_iterations": MAX_ITERATIONS,
            "usage": accumulated_usage,
        },
    }
