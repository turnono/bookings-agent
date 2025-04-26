"""Booking Validator Agent definition."""

import os
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from dotenv import load_dotenv

from bookings_agent.models import DEFAULT_MODEL
from bookings_agent.tools import current_time
from bookings_agent.tools.interact_with_firestore import sanitize_firestore_data
from bookings_agent.firestore_service import sanitize_sentinel
from bookings_agent.sub_agents.booking_validator.prompts import BOOKING_VALIDATOR_INSTRUCTION
from bookings_agent.tools import interact_with_firestore

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, "../../../.env"))

# Wrapper for interact_with_firestore specific to the booking validator agent
def booking_validator_interact_with_firestore(operation: str, args: dict) -> dict:
    """
    Wrapper for the interact_with_firestore tool that automatically adds the
    booking validator agent tag to memories and validations.
    
    Args:
        operation: The Firestore operation to perform
        args: The arguments for the operation
    
    Returns:
        The result of the Firestore operation
    """
    # Clean the args to ensure they're safe for Firestore
    clean_args = sanitize_firestore_data(args)
    
    # For memorize operations, ensure the agent is tagged
    if operation in ["memorize", "save_validation"]:
        # Add a tag for this agent
        if "tags" in clean_args and isinstance(clean_args["tags"], list):
            clean_args["tags"].append("agent:booking_validator")
        else:
            clean_args["tags"] = ["agent:booking_validator"]
    
    # Call the base interact_with_firestore tool
    result = interact_with_firestore(operation, clean_args)
    
    # Clean the result for return
    return sanitize_sentinel(result)

# Define the functions that would normally be passed as tools
# These are placeholders - actual implementations would need to be created
def validate_booking(date: str, time: str, duration: int, topic: str = None) -> dict:
    """
    Validate if an appointment can be booked at the specified date and time.
    Approve as soon as date, time, and topic are present and the slot is available (not a weekend or invalid date).
    """
    # Sample validation for calendar availability
    calendar_validation = {
        "is_available": True,
        "conflicts": [],
        "message": "Time slot is available"
    }

    from datetime import datetime
    try:
        booking_date = datetime.strptime(date, "%Y-%m-%d")
        if booking_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
            calendar_validation = {
                "is_available": False,
                "conflicts": ["weekend"],
                "message": "The requested date falls on a weekend when bookings are not available"
            }
    except ValueError:
        calendar_validation = {
            "is_available": False,
            "conflicts": ["invalid_date"],
            "message": "The provided date format is invalid"
        }

    # Always approve if required info is present and slot is available
    is_valid = bool(date and time and topic and calendar_validation["is_available"])

    topic_validation = {
        "is_relevant": True,
        "relevance_score": 100,
        "message": "Topic accepted."
    }

    return {
        "valid": is_valid,
        "topic_validation": topic_validation,
        "calendar_validation": calendar_validation,
        "message": f"Booking for {date} at {time} for {duration} minutes on topic '{topic}' is {'valid' if is_valid else 'invalid'}."
    }

def check_availability(date: str) -> dict:
    """
    Check the availability of time slots on a specified date.
    
    Args:
        date: The date to check in YYYY-MM-DD format
        
    Returns:
        A dictionary containing availability information
    """
    # This is a placeholder - actual implementation would check against a calendar
    
    # Sample blocked periods
    blocked_periods = []
    
    # For weekend check example
    from datetime import datetime
    try:
        check_date = datetime.strptime(date, "%Y-%m-%d")
        if check_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
            return {
                "available_slots": [],
                "blocked_periods": ["all_day"],
                "message": f"No availability on {date} as it falls on a weekend."
            }
    except ValueError:
        return {
            "available_slots": [],
            "blocked_periods": [],
            "message": "The provided date format is invalid."
        }
    
    # For weekdays, show some available slots
    return {
        "available_slots": [
            {"start": "09:00", "end": "10:00"},
            {"start": "11:00", "end": "12:00"},
            {"start": "14:00", "end": "15:00"}
        ],
        "blocked_periods": [
            {"start": "12:00", "end": "14:00", "reason": "lunch_break"},
            {"start": "15:00", "end": "16:00", "reason": "private_time"}
        ],
        "message": f"Available slots for {date} retrieved."
    }

def suggest_alternatives(date: str, time: str, duration: int, topic: str = None) -> dict:
    """
    Suggest alternative booking options when the requested one is not available.
    
    Args:
        date: The requested date in YYYY-MM-DD format
        time: The requested time in HH:MM format
        duration: The requested duration in minutes
        topic: The topic or purpose of the appointment
        
    Returns:
        A dictionary containing alternative booking options
    """
    # This is a placeholder - actual implementation would check against a calendar
    
    # Sample response for relevant topic but unavailable time
    if topic and topic.lower() in ["business consulting", "career coaching", "marketing strategy"]:
        from datetime import datetime, timedelta
        
        try:
            # Parse the requested date
            requested_date = datetime.strptime(date, "%Y-%m-%d")
            
            # If weekend, suggest next business day
            if requested_date.weekday() >= 5:
                next_monday = requested_date + timedelta(days=(7 - requested_date.weekday()))
                next_day_str = next_monday.strftime("%Y-%m-%d")
            else:
                # For weekday conflicts, suggest same day different time or next day
                next_day = requested_date + timedelta(days=1)
                next_day_str = next_day.strftime("%Y-%m-%d")
                
            return {
                "alternatives": [
                    {"date": date, "time": "11:00", "duration": duration, "message": "Earlier on the same day"},
                    {"date": date, "time": "14:00", "duration": duration, "message": "Afternoon on the same day"},
                    {"date": next_day_str, "time": time, "duration": duration, "message": "Same time next business day"}
                ],
                "message": f"Alternative booking options for {topic} appointment."
            }
        except ValueError:
            return {
                "alternatives": [],
                "message": "Cannot suggest alternatives due to invalid date format."
            }
    
    # For irrelevant topics, empty alternatives with explanation
    return {
        "alternatives": [],
        "message": "No alternatives are available as the topic does not match the owner's expertise."
    }

def return_to_guide(message: str) -> dict:
    """
    Return control to the main booking guide agent.
    
    Args:
        message: A message to pass to the guide agent
        
    Returns:
        A dictionary with transfer information
    """
    return {
        "transfer": True,
        "to_agent": "booking_guide",
        "message": message
    }

booking_validator_agent = LlmAgent(
    name="booking_validator",
    model=DEFAULT_MODEL,
    description="Validates booking requests, ensures they meet all requirements, and flags any issues or conflicts.",
    instruction=BOOKING_VALIDATOR_INSTRUCTION,
    tools=[
        FunctionTool(current_time),
        FunctionTool(booking_validator_interact_with_firestore),
        FunctionTool(validate_booking),
        FunctionTool(check_availability),
        FunctionTool(suggest_alternatives),
        FunctionTool(return_to_guide),
    ],
    output_key="booking_validator_output"
) 