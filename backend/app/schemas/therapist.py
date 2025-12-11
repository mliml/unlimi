from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class TherapistBase(BaseModel):
    """Base therapist model with common attributes."""
    name: str
    age: int
    info: str
    prompt: str


class TherapistRead(BaseModel):
    """Full therapist information returned to clients."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    age: int
    info: str
    prompt: str
    created_at: datetime
    updated_at: datetime


class TherapistUpdate(BaseModel):
    """Schema for updating therapist information."""
    name: Optional[str] = None
    age: Optional[int] = None
    info: Optional[str] = None
    prompt: Optional[str] = None


class TherapistListItem(BaseModel):
    """Simplified therapist information for list view."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    age: int
    info: str
