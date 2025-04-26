import os
from google.adk.agents import Agent, LlmAgent
from google.adk.tools import FunctionTool
from dotenv import load_dotenv
from typing import Optional

from bookings_agent.prompt import BOOKINGS_AGENT_INSTRUCTION
from bookings_agent.tools import current_time, interact_with_firestore
from bookings_agent.tools.interact_with_firestore import sanitize_firestore_data
from bookings_agent.firestore_service import sanitize_sentinel
from bookings_agent.models import DEFAULT_MODEL

from absl import logging
import uuid

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, "../.env"))

# Define the additional tools for the root booking guide agent
def validate_booking_request(booking_details: dict) -> dict:
    """
    ValidationTool: Validates an appointment request for topic relevance, user seriousness, and calendar availability.
    
    Args:
        booking_details: A dictionary containing booking details such as:
            - date: The requested date in YYYY-MM-DD format
            - time: The requested time in HH:MM format
            - duration: The appointment duration in minutes 
            - topic: The appointment purpose or topic
            - user_intent: Information about the user's motivation (optional)
            - user_id: User identifier (optional)
    
    Returns:
        A dictionary containing validation results
    """
    # This is a placeholder - the actual implementation would delegate to the validation agent
    
    # Basic validation of required fields
    if not all(k in booking_details for k in ["date", "time", "topic"]):
        return {
            "valid": False,
            "message": "Missing required booking information. Please provide date, time, and topic.",
            "validation_code": "MISSING_FIELDS"
        }
    
    # Example topic validation
    topic = booking_details.get("topic", "").lower()
    relevant_topics = ["business consulting", "career coaching", "marketing strategy", "business mentoring"]
    is_topic_relevant = any(t in topic for t in relevant_topics)
    
    # Example user intent validation
    user_intent = booking_details.get("user_intent", "")
    is_serious = len(user_intent) > 20 or "serious_intent" in booking_details
    
    # Combined validation
    is_valid = is_topic_relevant and is_serious
    
    return {
        "valid": is_valid,
        "is_topic_relevant": is_topic_relevant,
        "is_user_serious": is_serious,
        "suggested_next_step": "show_availability" if is_valid else "ask_qualifying_questions",
        "message": "Booking request is valid." if is_valid else "Please provide more information about your specific needs."
    }

def check_calendar_availability(date: str, appointment_type: Optional[str] = None, duration: int = 60) -> dict:
    """
    CalendarTool: Checks calendar availability for appointment bookings while respecting private time.
    
    Args:
        date: The date to check in YYYY-MM-DD format
        appointment_type: The type of appointment to check for (affects duration defaults)
        duration: The requested appointment duration in minutes
        
    Returns:
        A dictionary containing availability information
    """
    # This is a placeholder - the actual implementation would interact with a calendar API
    
    # Example appointment types and their default durations
    appointment_durations = {
        "initial_consultation": 60,
        "follow_up": 30,
        "strategy_session": 90,
        "quick_call": 15
    }
    
    # If appointment_type is provided, adjust duration
    if appointment_type and appointment_type in appointment_durations:
        duration = appointment_durations.get(appointment_type, duration)
    
    # Example of checking date
    from datetime import datetime
    try:
        booking_date = datetime.strptime(date, "%Y-%m-%d")
        # Example: Block weekends
        if booking_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
            return {
                "available_slots": [],
                "is_available": False,
                "blocked_periods": [{"all_day": True, "reason": "weekend"}],
                "message": f"No availability on {date} as it falls on a weekend. Please select a weekday."
            }
    except ValueError:
        return {
            "available_slots": [],
            "is_available": False,
            "message": "Invalid date format. Please use YYYY-MM-DD format."
        }
    
    # Example available slots for weekdays (would come from real calendar)
    available_slots = [
        {"start": "09:00", "end": "10:00", "buffer_required": 15},
        {"start": "10:30", "end": "11:30", "buffer_required": 15},
        {"start": "14:00", "end": "15:00", "buffer_required": 15},
        {"start": "15:30", "end": "16:30", "buffer_required": 15}
    ]
    
    # Example blocked periods (private time)
    blocked_periods = [
        {"start": "12:00", "end": "14:00", "reason": "lunch_and_personal_time"},
        {"start": "16:30", "end": "17:30", "reason": "admin_time"}
    ]
    
    return {
        "available_slots": available_slots,
        "blocked_periods": blocked_periods,
        "is_available": len(available_slots) > 0,
        "appointment_duration": duration,
        "message": f"Available slots for {date} retrieved, showing {len(available_slots)} options."
    }

def send_booking_confirmation(booking_id: str, recipient: str, booking_details: Optional[dict] = None) -> dict:
    """
    BookingConfirmationTool: Sends a booking confirmation with appointment details to the specified recipient.
    
    Args:
        booking_id: The ID of the booking to confirm
        recipient: The email address or identifier of the recipient
        booking_details: Optional dictionary with additional booking details to include
        
    Returns:
        A dictionary containing the confirmation status
    """
    # This is a placeholder - the actual implementation would send an email or notification
    
    # Example of confirmation details
    confirmation_details = {
        "appointment_confirmed": True,
        "booking_id": booking_id,
        "recipient": recipient,
        "confirmation_sent_at": current_time()["current_time"],
        "confirmation_method": "email",
        "calendar_invite_sent": True,
        "reminder_scheduled": True
    }
    
    # Add any provided booking details
    if booking_details:
        confirmation_details["details"] = booking_details
    
    return {
        "sent": True,
        "confirmation_details": confirmation_details,
        "message": f"Booking confirmation for appointment {booking_id} sent to {recipient}."
    }

root_agent = LlmAgent(
    name="booking_guide",
    model=DEFAULT_MODEL,
    description="Guides users from social media to book appointments, screens for relevance/seriousness, and protects calendar availability.",
    instruction=BOOKINGS_AGENT_INSTRUCTION,
    tools=[
        # MemoryTool (Firestore)
        FunctionTool(interact_with_firestore),
        # ValidationTool
        FunctionTool(validate_booking_request),
        # CalendarTool
        FunctionTool(check_calendar_availability),
        # BookingConfirmationTool
        FunctionTool(send_booking_confirmation)
    ],
    output_key="booking_guide_output"
)
