"""Logging hooks for agent lifecycle events."""

from typing import Any, Optional

from agents import (
    Agent,
    AgentHooks,
    RunContextWrapper,
    Tool,
    Usage,
)
from agents.items import ModelResponse, TResponseInputItem

from .config import logger


class LoggingHooks(AgentHooks):
    """Hooks for monitoring agent lifecycle events."""

    def _usage_to_str(self, usage: Usage) -> str:
        """Convert token Usage object to a formatted string."""
        return (
            f"{usage.requests} requests, {usage.input_tokens} input tokens, "
            f"{usage.output_tokens} output tokens, {usage.total_tokens} total tokens"
        )

    async def on_start(self, context: RunContextWrapper, agent: Agent) -> None:
        """Call before the agent is invoked."""
        logger.info(
            "(%s) Agent %s started. Usage: %s",
            agent.name,
            agent.name,
            self._usage_to_str(context.usage),
        )

    async def on_llm_start(
        self,
        context: RunContextWrapper,
        agent: Agent,
        system_prompt: Optional[str],
        input_items: list[TResponseInputItem],
    ) -> None:
        """Call just before invoking the LLM for the agent."""
        logger.info(
            "(%s) LLM started. Usage: %s", agent.name, self._usage_to_str(context.usage)
        )

    async def on_llm_end(
        self, context: RunContextWrapper, agent: Agent, response: ModelResponse
    ) -> None:
        """Call immediately after the LLM call returns for the agent."""
        logger.info(
            "(%s) LLM ended. Usage: %s", agent.name, self._usage_to_str(context.usage)
        )

    async def on_end(
        self, context: RunContextWrapper, agent: Agent, output: Any
    ) -> None:
        """Call when the agent produces a final output."""
        logger.info(
            "(%s) Agent %s ended with output %s. Usage: %s",
            agent.name,
            agent.name,
            output,
            self._usage_to_str(context.usage),
        )

    async def on_tool_start(
        self, context: RunContextWrapper, agent: Agent, tool: Tool
    ) -> None:
        """Call immediately before a local tool is invoked."""
        logger.info(
            "(%s) Tool %s started. name=%s, call_id=%s, args=%s. Usage: %s",
            agent.name,
            tool.name,
            context.tool_name,  # type: ignore[attr-defined]
            context.tool_call_id,  # type: ignore[attr-defined]
            context.tool_arguments,  # type: ignore[attr-defined]
            self._usage_to_str(context.usage),
        )

    async def on_tool_end(
        self, context: RunContextWrapper, agent: Agent, tool: Tool, result: str
    ) -> None:
        """Call immediately after a local tool is invoked."""
        logger.info(
            "(%s) Tool %s finished. result=%s, name=%s, call_id=%s, args=%s. Usage: %s",
            agent.name,
            tool.name,
            result,
            context.tool_name,  # type: ignore[attr-defined]
            context.tool_call_id,  # type: ignore[attr-defined]
            context.tool_arguments,  # type: ignore[attr-defined]
            self._usage_to_str(context.usage),
        )

    async def on_handoff(
        self, context: RunContextWrapper, from_agent: Agent, to_agent: Agent
    ) -> None:
        """Call when a handoff occurs."""
        logger.info(
            "(%s) Handoff from %s to %s. Usage: %s",
            from_agent.name,
            from_agent.name,
            to_agent.name,
            self._usage_to_str(context.usage),
        )
