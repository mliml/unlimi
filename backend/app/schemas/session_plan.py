from pydantic import BaseModel, ConfigDict
from datetime import datetime


class SessionPlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    plan_text: str
    created_at: datetime
