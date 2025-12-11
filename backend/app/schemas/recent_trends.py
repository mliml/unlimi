from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Dict, Any


class RecentTrendsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    trends_json: Dict[str, Any]
    updated_at: datetime
