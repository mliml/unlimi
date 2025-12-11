from pydantic import BaseModel
from datetime import datetime


class UserContextResponse(BaseModel):
    """用户上下文响应"""
    context_text: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
