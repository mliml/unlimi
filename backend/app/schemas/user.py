from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base user model with common attributes."""
    email: EmailStr


class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    """Public user information returned to clients (no sensitive data)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    nickname: Optional[str] = None
    therapist_id: str
    created_at: datetime
    updated_at: datetime


class UserRead(BaseModel):
    """Full user information (for internal use)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    nickname: Optional[str] = None
    therapist_id: str
    has_finished_onboarding: bool
    created_at: datetime
    updated_at: datetime


class UserOverview(BaseModel):
    """User overview information for homepage."""
    email: str
    nickname: Optional[str] = None
    therapist_id: str
    has_finished_onboarding: bool
    total_sessions: int
    last_session_time: Optional[datetime]
    next_plan: Optional[str]


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    nickname: Optional[str] = None
    therapist_id: Optional[str] = None
