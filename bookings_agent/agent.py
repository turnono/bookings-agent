import os
from google.adk.agents import Agent, LlmAgent
from dotenv import load_dotenv
from typing import Optional

from bookings_agent.models import DEFAULT_MODEL
from bookings_agent.tools.google_calendar import list_upcoming_events, create_event
from google.adk.tools import FunctionTool


BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, "../.env"))


root_agent = LlmAgent(
    name="booking_guide",
    model=DEFAULT_MODEL,
    description="Guides users to book appointments and checks calendar availability.",
    instruction=(
        "You are a booking agent. You help users book appointments and check calendar availability. "
        "When a user asks to see calendar events, use the list_upcoming_events tool with calendar_id='turnono@gmail.com' "
        "and max_results=10 unless the user specifies otherwise. "
        "When a user asks to create a calendar event, use the create_event tool with the details they provide. "
        "If any required information is missing, ask the user for it."
    ),
    tools=[
        FunctionTool(list_upcoming_events),
        FunctionTool(create_event),
    ],
    output_key="booking_guide_output"
)
