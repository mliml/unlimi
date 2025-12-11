from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.db.models.session import SessionStatus


class SessionCreate(BaseModel):
    user_id: int


class SessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    start_time: datetime
    end_time: Optional[datetime]
    status: SessionStatus


class SessionDetail(BaseModel):
    """Detailed session information without full message history."""
    id: int
    start_time: datetime
    end_time: Optional[datetime]
    is_closed: bool
    message_count: int
    review_text: Optional[str]
    key_events: List[str]
    plan_text: Optional[str]

    # Session timing and turn control (for debugging)
    active_duration_seconds: int
    turn_count: int
    overtime_reminder_count: int
    should_remind: bool = False  # Whether timeout reminder should be shown


class SessionHistoryItem(BaseModel):
    """History session item for the history list endpoint."""
    id: int
    start_time: datetime
    end_time: Optional[datetime]
    message_count: int
    index: int
