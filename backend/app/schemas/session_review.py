from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class SessionReviewResponse(BaseModel):
    """Session review response for the consultation review tab."""
    session_id: int
    start_time: datetime
    end_time: Optional[datetime]
    message_count: int
    session_review: Optional[str]
    key_events: List[str] = []
