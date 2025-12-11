from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Dict, Any


class UserInsightsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    insights_json: Dict[str, Any]
    updated_at: datetime
