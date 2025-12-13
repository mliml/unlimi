from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.services.database import Base


class SessionStatus(str, enum.Enum):
    open = "open"
    closed = "closed"


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    agno_session_id = Column(String(255), nullable=True, index=True)  # 关联 Agno session
    start_time = Column(DateTime, server_default=func.now(), nullable=False)
    end_time = Column(DateTime, nullable=True)
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.open, nullable=False)

    # 会话时间和轮数控制
    active_duration_seconds = Column(Integer, default=0, nullable=False)  # 累计活跃时长（秒）
    turn_count = Column(Integer, default=0, nullable=False)  # 对话往返轮数
    overtime_reminder_count = Column(Integer, default=0, nullable=False)  # 超时提示次数

    # Relationships
    user = relationship("User", back_populates="sessions")
    review = relationship("SessionReview", back_populates="session", uselist=False, cascade="all, delete-orphan")
    messages = relationship("SessionMessage", back_populates="session", cascade="all, delete-orphan", order_by="SessionMessage.created_at")  # 待迁移后删除
    plan = relationship("SessionPlan", back_populates="session", uselist=False, cascade="all, delete-orphan")  # Reserved for future use
    emo_scores = relationship("EmoScore", back_populates="session", cascade="all, delete-orphan")
