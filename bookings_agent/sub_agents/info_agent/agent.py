from google.adk.agents import LlmAgent
from bookings_agent.sub_agents.info_agent.prompts import INFO_AGENT_PROMPT
from bookings_agent.models import DEFAULT_MODEL

info_agent = LlmAgent(
    name="info_agent",
    model=DEFAULT_MODEL,
    description="Introduces services and answers common questions for new users.",
    instruction=INFO_AGENT_PROMPT,
    output_key="info_output"
) 