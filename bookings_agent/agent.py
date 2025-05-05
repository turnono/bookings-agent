import os
from google.adk.agents import Agent, LlmAgent
from dotenv import load_dotenv
from typing import Optional

from bookings_agent.models import DEFAULT_MODEL
from bookings_agent.prompts import ROOT_AGENT_PROMPT
from bookings_agent.tools.google_calendar import create_event, get_available_time_slots
from bookings_agent.sub_agents.booking_validator import booking_validator_agent
from bookings_agent.sub_agents.inquiry_collector import inquiry_collector_agent
from bookings_agent.sub_agents.info_agent import info_agent
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool
from bookings_agent.sub_agents.intent_extractor import intent_extractor_agent
from bookings_agent.tools.validate_email import validate_email


# Conversation Management for Booking Agent:
# - The agent encourages quick progression toward booking without pressuring the user.
# - Light hints are given after several exchanges to maintain focus.
# - Long, off-topic inputs are politely redirected toward summarization.
# - No hard limits are shown to the user — all restrictions are applied subtly to preserve a professional and welcoming experience.

AGENT_SUMMARY = (
    "I am your booking assistant, helping others quickly find and confirm a session tailored to their needs. "
    "I ensure a smooth, respectful, and secure experience, from validation to booking to confirmation."
)

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, "../.env"))

root_agent = LlmAgent(
    name="bookings_agent",
    model=DEFAULT_MODEL,
    description="Helps others find and confirm a session with Abdullah Abrahams tailored to their needs, from validation to booking to confirmation",
    instruction=ROOT_AGENT_PROMPT,
    sub_agents=[
        booking_validator_agent,
        inquiry_collector_agent,
        info_agent,
    ],
    tools=[
        FunctionTool(create_event),
        FunctionTool(get_available_time_slots),
        FunctionTool(validate_email),
        AgentTool(intent_extractor_agent),
    ],
    output_key="bookings_agent_output"
)
