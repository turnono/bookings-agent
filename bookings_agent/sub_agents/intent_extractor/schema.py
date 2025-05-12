"""
Pydantic schemas for the intent extractor agent.

This module defines the structured data schema for the intent extractor's output,
ensuring that responses follow the expected format.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional


class IntentOutput(BaseModel):
    """
    Schema for the intent extractor's output.
    
    Defines the expected format for the intent classification result:
    - intent: The category of user intent (booking, info, inquiry, other)
    - topic: A short phrase describing the topic or empty string
    - confidence: A confidence score for the classification (0.0-1.0)
    """
    intent: Literal["booking", "info", "inquiry", "other"] = Field(
        description="The extracted intent category")
    topic: str = Field(
        description="A short phrase summarizing the topic or empty string")
    confidence: float = Field(
        description="Classification confidence score between 0.0 and 1.0",
        ge=0.0, le=1.0)
    
    @field_validator('confidence')
    def validate_confidence(cls, v):
        """Ensure confidence is within 0.0-1.0 range"""
        if v < 0.0 or v > 1.0:
            raise ValueError('Confidence must be between 0.0 and 1.0')
        return v 