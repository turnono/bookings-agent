import os
from google.adk.agents import Agent, LlmAgent
from dotenv import load_dotenv
from typing import Optional

from bookings_agent.models import DEFAULT_MODEL
from bookings_agent.tools.google_calendar import create_event, get_available_time_slots
from bookings_agent.sub_agents.booking_validator import validator_agent
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
    "I am your booking assistant, helping you quickly find and confirm a session tailored to your needs. "
    "I ensure a smooth, respectful, and secure experience, from validation to booking to confirmation."
)

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, "../.env"))

root_agent = LlmAgent(
    name="booking_guide",
    model=DEFAULT_MODEL,
    description="Guides users to book appointments and checks calendar availability.",
    instruction=(
        AGENT_SUMMARY + "\n"
        "Booking Flow: "
        "1. After the user's first message, immediately analyze it using the intent_extractor_agent to determine intent."
        "2. Based on the intent, transfer the user to the appropriate agent:"
        "   - For 'booking' intent: Transfer to the validator_agent for screening."
        "   - For 'info' intent: Transfer to the info_agent."
        "   - For 'inquiry' intent: Transfer to the inquiry_collector_agent."
        "   - For 'other' intent: Continue with the default booking flow."
        "3. The Validator Agent screens the user for topic and seriousness. "
        "4. After validation, proceed to scheduling the consultation. "
        "5. Ask the user for their preferred dates (not times), e.g., 'Which dates between [date] and [date] would suit you?' "
        "6. Parse natural language date phrases (today, tomorrow, next week, this week, from today, from tomorrow) to concrete date ranges using the current year as default. "
        "7. Assume sessions are 30 minutes unless the user specifies otherwise. Only ask about session length if unclear. "
        "8. Fetch available slots for those dates and show them to the user for selection. Do not ask the user to guess times manually. "
        "9. After the user selects a slot, ask for their email address and validate it using the validate_email tool. "
        "10. Create the calendar event directly using the create_event tool with:"
        "    - summary: 'Consultation with Abdullah Abrahams'"
        "    - start_time: the selected slot"
        "    - end_time: 30 minutes after start_time"
        "    - description: the topic"
        "    - attendees: the user's email address"
        "11. Once the calendar event is created, inform the user that their booking is confirmed and that they'll receive a calendar invitation."
        "    - If the calendar event creation returns an 'attendees_warning', explain to the user that they will need to be added to the invitation manually."
        "\nConversation Management: "
        "- Encourage polite, quick progression toward booking. "
        "- Give subtle hints if the conversation goes off-track. "
        "- Summarize long or off-topic user inputs internally. "
        "- Never show hard character limits to the user. "
        "\nRouting Additions: "
        "After every sub-agent call, inspect for these keys in the response: "
        "• handoff_to_consultation "
        "• handoff_to_opportunities "
        "• screening_result "
        "• inquiry_saved "
        "Then immediately route to the next step based on whichever key is present. If none are present, continue the same agent's flow. "
    ),
    sub_agents=[
        validator_agent,
        inquiry_collector_agent,
        info_agent,
    ],
    tools=[
        FunctionTool(create_event),
        FunctionTool(get_available_time_slots),
        FunctionTool(validate_email),
        AgentTool(intent_extractor_agent),
    ],
    output_key="booking_guide_output"
)
