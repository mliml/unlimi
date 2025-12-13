from pydantic import BaseModel, Field
from typing import Optional, List
from app.models.user_onboarding import QuestionType
from app.schemas.emo_score import EmoScoreResponse


class OnboardingQuestionResponse(BaseModel):
    """单个问题的响应"""
    question_number: int
    question_text: str
    question_type: QuestionType
    options: Optional[List[str]] = None


class OnboardingStateResponse(BaseModel):
    """获取当前状态的响应 (GET /onboarding)"""
    is_complete: bool
    session_id: Optional[str] = None
    question: Optional[OnboardingQuestionResponse] = None
    message: Optional[str] = None


class OnboardingAnswerRequest(BaseModel):
    """提交答案的请求"""
    session_id: str
    question_number: int
    answer: str


class OnboardingAnswerResponse(BaseModel):
    """提交答案的响应"""
    is_complete: bool
    next_question: Optional[OnboardingQuestionResponse] = None

    # 以下字段仅在 is_complete=True 时返回
    emo_score: Optional[EmoScoreResponse] = None
    user_context: Optional[str] = None
    nickname: Optional[str] = None
    total_questions: Optional[int] = None
