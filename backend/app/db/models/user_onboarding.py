from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class QuestionType(str, enum.Enum):
    """问题类型"""
    CHOICE = "choice"  # 选择题
    TEXT = "text"      # 问答题


class UserOnboarding(Base):
    """
    User onboarding questionnaire responses.

    支持动态问题生成，包含选择题和问答题两种类型。
    每个用户有 5-10 条记录（每个问题一条）。
    """
    __tablename__ = "user_onboardings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # 问题序号（1-10）
    question_number = Column(Integer, nullable=False)

    # 问题内容
    question_text = Column(Text, nullable=False)

    # 问题类型
    question_type = Column(Enum(QuestionType, values_callable=lambda x: [e.value for e in x]), nullable=False)

    # 选择题选项（JSON 数组，如 ["选项A", "选项B", "选项C"]）
    # 问答题时为 null
    question_options = Column(JSON, nullable=True)

    # 用户回答（文本答案或选中的选项）
    answer = Column(Text, nullable=True)

    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    answered_at = Column(DateTime, nullable=True)  # 用户回答时间

    # Relationships
    user = relationship("User", back_populates="onboardings")
