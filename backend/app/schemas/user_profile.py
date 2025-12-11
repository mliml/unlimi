from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Dict, Any


class UserProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    profile_json: Dict[str, Any]
    updated_at: datetime
