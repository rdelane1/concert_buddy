"""A sub-agent specializing in searching for concert event information."""

from datetime import datetime

from agents import Agent, ModelSettings, WebSearchTool
from openai.types.shared import Reasoning
from pydantic import BaseModel

from ..core.config import get_settings
from ..hooks import LoggingHooks

app_settings = get_settings()

class Concert(BaseModel):
    """A live concert event."""

    headline_artist: str | None = None
    """The main artist or band performing at the concert."""

    supporting_acts: list[str] | None = None
    """A list of supporting acts or opening bands, if any."""

    venue: str | None = None
    """The name of the venue where the concert will take place."""

    city: str | None = None
    """The city where the concert will be held."""

    date: str | None = None
    """The date of the concert."""


# A sub-agent specializing on searching for concert event information
CONCERT_INSTRUCTIONS = f"""You are a live concert agent. You are highly
capable of searching the web for information about upcoming live concert events.
Your task is to search for an upcoming live concert event based on a user's
request. Users will describe the event they are interested in,
providing details such as artist or band name, and city. If you find an event
that matches the user's description, you return the event details.
If there is no upcoming event matching the user's request, respond with an empty output.
You always provide up-to-date information on upcoming events and never
provide information for past events. For reference, today's date
is {datetime.now().strftime("%B %d, %Y")}.
"""

concert_agent = Agent(
    name="Concert Agent",
    instructions=CONCERT_INSTRUCTIONS,
    model=app_settings.concert_agent_model,
    model_settings=ModelSettings(
        reasoning=Reasoning(effort=app_settings.concert_agent_reasoning_effort),
        verbosity=app_settings.concert_agent_verbosity
    ),
    output_type=Concert,
    tools=[WebSearchTool()],
    hooks=LoggingHooks(),
)
