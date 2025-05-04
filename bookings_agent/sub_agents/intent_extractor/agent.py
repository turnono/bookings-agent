from google.adk.agents import LlmAgent
from bookings_agent.sub_agents.intent_extractor.prompts import INTENT_EXTRACTOR_PROMPT
from bookings_agent.models import DEFAULT_MODEL

intent_extractor_agent = LlmAgent(
    name="intent_extractor",
    model=DEFAULT_MODEL,
    description="Extracts the intent and topic from the user message.",
    instruction=INTENT_EXTRACTOR_PROMPT,
    output_key="intent_extractor_output"
) 