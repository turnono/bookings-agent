import os
from google.adk.agents import LlmAgent
from bookings_agent.sub_agents.booking_validator.prompts import BOOKING_VALIDATOR_PROMPT
from bookings_agent.models import DEFAULT_MODEL

validator_agent = LlmAgent(
    name="booking_validator",
    model=DEFAULT_MODEL,
    description="Screens users for topic relevance before booking.",
    instruction=BOOKING_VALIDATOR_PROMPT,
    output_key="validator_output"
) 