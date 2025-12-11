from pydantic import BaseModel, ConfigDict
from datetime import datetime


class SessionSummaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    summary_text: str
    created_at: datetime
