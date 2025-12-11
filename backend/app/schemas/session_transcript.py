from pydantic import BaseModel, ConfigDict
from datetime import datetime


class SessionTranscriptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    transcript: str
    created_at: datetime
