"""Logging hooks for agent run lifecycle events."""

from typing import Any, Optional

from agents import (
    Agent,
    RunContextWrapper,
    RunHooks,
    Tool,
    Usage,
)
from agents.items import ModelResponse, TResponseInputItem


class LoggingHooks(RunHooks):
    """Hooks for monitoring agent run lifecycle events."""

    def __init__(self):
        """Initialize the logging hooks."""
        pass

    def _usage_to_str(self, usage: Usage) -> str:
        """Convert token Usage object to a formatted string."""
        return (
            f"{usage.requests} requests, {usage.input_tokens} input tokens, "
            f"{usage.output_tokens} output tokens, {usage.total_tokens} total tokens"
        )

    async def on_agent_start(self, context: RunContextWrapper, agent: Agent) -> None:
        """Call before the agent is invoked."""
        print(
            f"({agent.name}) Agent {agent.name} started. "
            f"Usage: {self._usage_to_str(context.usage)}"
        )

    async def on_llm_start(
        self,
        context: RunContextWrapper,
        agent: Agent,
        system_prompt: Optional[str],
        input_items: list[TResponseInputItem],
    ) -> None:
        """Call just before invoking the LLM for the agent."""
        print(f"({agent.name}) LLM started. Usage: {self._usage_to_str(context.usage)}")

    async def on_llm_end(
        self, context: RunContextWrapper, agent: Agent, response: ModelResponse
    ) -> None:
        """Call immediately after the LLM call returns for the agent."""
        print(f"({agent.name}) LLM ended. Usage: {self._usage_to_str(context.usage)}")

    async def on_agent_end(
        self, context: RunContextWrapper, agent: Agent, output: Any
    ) -> None:
        """Call when the agent produces a final output."""
        print(
            f"({agent.name}) Agent {agent.name} ended with "
            f"output {output}. Usage: {self._usage_to_str(context.usage)}"
        )

    async def on_tool_start(
        self, context: RunContextWrapper, agent: Agent, tool: Tool
    ) -> None:
        """Call immediately before a local tool is invoked."""
        print(
            f"({agent.name}) Tool {tool.name} started. "
            f"name={context.tool_name}, call_id={context.tool_call_id}, "  # type: ignore[attr-defined]
            f"args={context.tool_arguments}. "  # type: ignore[attr-defined]
            f"Usage: {self._usage_to_str(context.usage)}"
        )

    async def on_tool_end(
        self, context: RunContextWrapper, agent: Agent, tool: Tool, result: str
    ) -> None:
        """Call immediately after a local tool is invoked."""
        print(
            f"({agent.name}) Tool {tool.name} finished. "
            f"result={result}, name={context.tool_name}, "  # type: ignore[attr-defined]
            f"call_id={context.tool_call_id}, "  # type: ignore[attr-defined]
            f"args={context.tool_arguments}. "  # type: ignore[attr-defined]
            f"Usage: {self._usage_to_str(context.usage)}"
        )

    async def on_handoff(
        self, context: RunContextWrapper, from_agent: Agent, to_agent: Agent
    ) -> None:
        """Call when a handoff occurs."""
        print(
            f"({from_agent.name}) Handoff from {from_agent.name} to "
            f"{to_agent.name}. Usage: {self._usage_to_str(context.usage)}"
        )
