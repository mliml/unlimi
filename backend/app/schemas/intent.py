"""
Intent classification schemas for user message intent recognition.
"""
from pydantic import BaseModel, Field
from typing import Literal


class IntentResult(BaseModel):
    """
    Result of intent classification for a user message.

    Attributes:
        intent: The classified intent type (NORMAL, END_SESSION, or CRISIS)
        confidence: Confidence score of the classification (0.0 to 1.0)
    """
    intent: Literal["NORMAL", "END_SESSION", "CRISIS"] = Field(
        ...,
        description="The classified intent of the user message"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score of the classification"
    )
