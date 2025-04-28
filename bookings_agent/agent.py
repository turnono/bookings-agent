import os
from google.adk.agents import Agent, LlmAgent
from dotenv import load_dotenv
from typing import Optional

from bookings_agent.models import DEFAULT_MODEL
from bookings_agent.tools.google_calendar import create_event, get_available_time_slots
from bookings_agent.sub_agents.booking_validator import validator_agent
from bookings_agent.sub_agents.inquiry_collector import inquiry_collector_agent
from bookings_agent.sub_agents.payment_agent import payment_agent
from bookings_agent.sub_agents.payment_agent.agent import create_paystack_checkout
from google.adk.tools import FunctionTool
from bookings_agent.booking_flow import handle_payment_confirmed


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

def payment_confirmation_flow(booking_id: str, user_id: str) -> str:
    """
    Agent tool: When payment_confirmed is detected, call this to create the event and notify the user.
    """
    return handle_payment_confirmed(booking_id, user_id)

root_agent = LlmAgent(
    name="booking_guide",
    model=DEFAULT_MODEL,
    description="Guides users to book appointments and checks calendar availability.",
    instruction=(
        AGENT_SUMMARY + "\n"
        "Booking Flow: "
        "1. The Validator Agent screens the user for topic and seriousness. "
        "2. After validation, remind the user that sessions are paid consultations. "
        "3. Ask the user for their preferred dates (not times), e.g., 'Which dates between [date] and [date] would suit you?' "
        "4. Parse natural language date phrases (today, tomorrow, next week, this week, from today, from tomorrow) to concrete date ranges using the current year as default. "
        "5. Assume sessions are 30 minutes unless the user specifies otherwise. Only ask about session length if unclear. "
        "6. Fetch available slots for those dates and show them to the user for selection. Do not ask the user to guess times manually. "
        "7. When the user selects a slot, hold it internally as 'pending' (do not create the calendar event yet). Log the user's topic and tags in Firestore with the booking. "
        "8. Send the user to payment and instruct them to pay within 10 minutes to confirm. "
        "9. If payment succeeds, create the Google Calendar event and send booking confirmation. "
        "10. If payment fails or times out, release the held slot and inform the user politely. "
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
        "• payment_confirmed "
        "• payment_rejected "
        "• inquiry_saved "
        "Then immediately route to the next step based on whichever key is present. If none are present, continue the same agent's flow. "
        "\nIf you see payment_confirmed, call the payment_confirmation_flow tool with the bookingId and userId."
    ),
    sub_agents=[
        validator_agent,
        inquiry_collector_agent,
        payment_agent,
    ],
    tools=[
        FunctionTool(create_event),
        FunctionTool(get_available_time_slots),
        FunctionTool(create_paystack_checkout),
        FunctionTool(payment_confirmation_flow),
    ],
    output_key="booking_guide_output"
)
