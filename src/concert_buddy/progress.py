"""Progress reporting via Server-Sent Events (SSE)."""

import asyncio
import json
from collections import defaultdict
from typing import AsyncGenerator

from agents import function_tool

# In-memory event queues per session
_EVENT_QUEUES: dict[str, asyncio.Queue[str]] = defaultdict(asyncio.Queue)


def get_queue(session_id: str) -> asyncio.Queue[str]:
    """Get or create the event queue for a session."""
    if session_id not in _EVENT_QUEUES:
        _EVENT_QUEUES[session_id] = asyncio.Queue()
    return _EVENT_QUEUES[session_id]


async def publish_event(session_id: str, event: dict) -> None:
    """Publish an event (as JSON string) to the session queue."""
    await get_queue(session_id).put(json.dumps(event))


async def sse_event_stream(session_id: str) -> AsyncGenerator[bytes, None]:
    """Yield events for a session using a simple SSE generator."""
    queue = get_queue(session_id)
    # Send an initial heartbeat so clients connect promptly
    yield b":ok\n\n"
    while True:
        data = await queue.get()
        yield f"data: {data}\n\n".encode()


@function_tool
async def report_todos(session_id: str, todos: list[str]) -> str:
    """Report the initial TODO list for a session.

    Args:
        session_id: The session identifier provided by the server.
        todos: An ordered list of step descriptions.

    Returns:
        Confirmation string.

    """
    await publish_event(session_id, {"type": "todos", "todos": todos})
    return "reported_todos"


@function_tool
async def update_todo(
    session_id: str, todo: str, status: str, message: str | None = None
) -> str:
    """Send a progress update for a single TODO item.

    Args:
        session_id: The session identifier provided by the server.
        todo: The textual description of the TODO this update refers to.
        status: One of: pending | in_progress | done | error.
        message: Optional additional info for the user.

    """
    await publish_event(
        session_id,
        {
            "type": "todo_update",
            "todo": todo,
            "status": status,
            "message": message,
        },
    )
    return "updated_todo"
