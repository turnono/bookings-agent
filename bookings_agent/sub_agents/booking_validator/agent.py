import os
from google.adk.agents import LlmAgent
from bookings_agent.sub_agents.booking_validator.prompts import BOOKING_VALIDATOR_PROMPT
from bookings_agent.models import DEFAULT_MODEL
from bookings_agent.sub_agents.booking_validator.schema import BookingValidationOutput

booking_validator_agent = LlmAgent(
    name="booking_validator",
    model=DEFAULT_MODEL,
    description="Screens users for topic relevance then hands off to the appropriate agent.",
    instruction=BOOKING_VALIDATOR_PROMPT,
    output_schema=BookingValidationOutput,
    output_key="booking_validator_output"
) 