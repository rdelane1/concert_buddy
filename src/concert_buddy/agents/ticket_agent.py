"""Agent specializing in searching for concert tickets."""

from datetime import datetime

from agents import Agent, ModelSettings, WebSearchTool
from openai.types.shared import Reasoning

from ..hooks import LoggingHooks

# A sub-agent specializing on searching for concert tickets
TICKET_INSTRUCTIONS = f"""You are a concert ticket agent.
You are skilled in navigating the web to find concert ticket information.
You will be provided with a concert event description and your task is to search
for available tickets from trusted, official ticket vendors.
Your output should include the types of tickets available
(e.g., general admission, VIP), their prices, and a link where the user
can purchase the tickets.
You only provide ticket information from trusted, official ticket vendors.
If tickets are sold out or unavailable, politely inform the user in your response.
You always provide up-to-date information on ticket availability and pricing.
You never provide information for past events.
For reference, today's date is {datetime.now().strftime("%B %d, %Y")}.
"""

ticket_agent = Agent(
    name="Ticket Agent",
    instructions=TICKET_INSTRUCTIONS,
    model="gpt-5",
    model_settings=ModelSettings(reasoning=Reasoning(effort="low"), verbosity="low"),
    tools=[WebSearchTool()],
    hooks=LoggingHooks(),
)
