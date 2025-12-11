from pydantic import BaseModel
from typing import List, Optional


class SessionStartResponse(BaseModel):
    """Response schema for starting a new session"""
    session_id: int


class SessionEndResponse(BaseModel):
    """Response schema for ending a session"""
    session_id: int
    session_review: Optional[str] = None
    key_events: List[str] = []


class ActiveSessionResponse(BaseModel):
    """Response schema for checking active session"""
    active: bool
    session_id: Optional[int] = None
