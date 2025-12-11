from pydantic import BaseModel
from typing import List, Optional


class UserMemoryItem(BaseModel):
    """User memory item from Agno framework"""
    memory_id: str
    memory: str
    topics: List[str]
    created_at: Optional[str]
    updated_at: Optional[str]
