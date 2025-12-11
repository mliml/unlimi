"""
Invitation Code Schemas

Pydantic models for invitation code management.
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class InvitationCodeResponse(BaseModel):
    """Response model for invitation code."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    is_universal: bool
    is_used: bool
    used_by_email: Optional[str] = None
    used_at: Optional[datetime] = None
    created_at: datetime


class InvitationCodeListResponse(BaseModel):
    """Response model for list of invitation codes."""
    codes: list[InvitationCodeResponse]
