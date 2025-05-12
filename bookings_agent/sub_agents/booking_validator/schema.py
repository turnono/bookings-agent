"""
Pydantic schemas for the booking validator agent.

This module defines the structured data schema for the booking validator's output,
ensuring that responses follow the expected format.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional


class BookingValidationOutput(BaseModel):
    """
    Schema for the booking validator's output.
    
    Defines the expected format for the booking validation result:
    - screening_result: Whether the booking request is accepted or rejected
    - handoff_to_inquiry: Whether to redirect to the inquiry agent
    - handoff_to_info: Whether to redirect to the info agent
    - need_topic_clarification: Whether the user needs to specify a topic
    - topic: The validated topic (if provided)
    - rejection_reason: The reason for rejection (if applicable)
    """
    screening_result: Literal["accepted", "rejected"] = Field(
        description="Whether the booking request passes screening")
    handoff_to_inquiry: bool = Field(
        description="Whether to redirect to the inquiry agent", 
        default=False)
    handoff_to_info: bool = Field(
        description="Whether to redirect to the info agent", 
        default=False)
    need_topic_clarification: bool = Field(
        description="Whether the user needs to specify a topic", 
        default=False)
    topic: Optional[str] = Field(
        description="The validated topic if provided", 
        default=None)
    rejection_reason: Optional[str] = Field(
        description="Reason for rejection if applicable", 
        default=None) 