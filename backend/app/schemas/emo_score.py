from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from app.models.emo_score import EmoScoreSource


class EmoScoreCreate(BaseModel):
    """创建情绪评估的请求 schema"""
    stress_score: Optional[int] = Field(None, ge=1, le=100, description="压力分数 (1-100)")
    stable_score: Optional[int] = Field(None, ge=1, le=100, description="稳定度分数 (1-100)")
    anxiety_score: Optional[int] = Field(None, ge=1, le=100, description="焦虑分数 (1-100)")
    functional_score: Optional[int] = Field(None, ge=1, le=100, description="功能分数 (1-100)")
    source: EmoScoreSource = Field(..., description="评估来源 (onboarding/session)")
    session_id: Optional[int] = Field(None, description="会话 ID（source=session 时必填）")


class EmoScoreResponse(BaseModel):
    """情绪评估的响应 schema"""
    id: int
    user_id: int

    stress_score: Optional[int] = None
    stable_score: Optional[int] = None
    anxiety_score: Optional[int] = None
    functional_score: Optional[int] = None

    stress_score_change: Optional[float] = None
    stable_score_change: Optional[float] = None
    anxiety_score_change: Optional[float] = None
    functional_score_change: Optional[float] = None

    source: EmoScoreSource
    session_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class EmoScoreListResponse(BaseModel):
    """评估历史列表响应"""
    total: int
    items: list[EmoScoreResponse]
