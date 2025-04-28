from google.adk.agents import LlmAgent
from bookings_agent.sub_agents.intro_agent.prompts import INTRO_AGENT_PROMPT
from bookings_agent.models import DEFAULT_MODEL

intro_agent = LlmAgent(
    name="intro_agent",
    model=DEFAULT_MODEL,
    description="Introduces services and answers common questions for new users.",
    instruction=INTRO_AGENT_PROMPT,
    output_key="intro_output"
) 