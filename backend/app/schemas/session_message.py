from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SessionMessageRequest(BaseModel):
    """Request schema for sending a message in a session"""
    message: str = Field(..., min_length=1, description="User message content")
    active_duration_seconds: Optional[int] = Field(None, description="Accumulated active duration in seconds (from frontend timer)")


class SessionMessageResponse(BaseModel):
    """Response schema for therapist reply"""
    reply: str = Field(..., description="Therapist's response")


class SessionMessageListItem(BaseModel):
    """Response schema for a single message in session message list"""
    id: int = Field(..., description="Message ID")
    sender: str = Field(..., description="Message sender: user, therapist, or system")
    message: str = Field(..., description="Message content")
    created_at: datetime = Field(..., description="Timestamp when message was created")

    class Config:
        from_attributes = True
