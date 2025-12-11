from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class EmoScoreSource(str, enum.Enum):
    """评估来源类型"""
    ONBOARDING = "onboarding"    # 用户引导阶段评估
    SESSION = "session"          # 会话期间评估


class EmoScore(Base):
    """
    用户情绪分数评估记录（时间序列）

    存储用户的四个情绪分数及其变化率的历史记录。
    每次评估创建一条新记录，不支持修改/删除（append-only）。
    """
    __tablename__ = "user_emo_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # 四个情绪分数 (1-100, nullable)
    stress_score = Column(Integer, nullable=True)          # 压力分数
    stable_score = Column(Integer, nullable=True)          # 稳定度分数
    anxiety_score = Column(Integer, nullable=True)         # 焦虑分数
    functional_score = Column(Integer, nullable=True)      # 功能分数

    # 变化率 (Float, nullable, 如 0.2 表示增长 20%, -0.15 表示下降 15%)
    stress_score_change = Column(Float, nullable=True)
    stable_score_change = Column(Float, nullable=True)
    anxiety_score_change = Column(Float, nullable=True)
    functional_score_change = Column(Float, nullable=True)

    # 评估来源
    source = Column(
        Enum(EmoScoreSource, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True
    )

    # 关联的会话 ID（仅当 source=SESSION 时有值）
    session_id = Column(
        Integer,
        ForeignKey("sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="emo_scores")
    session = relationship("Session", back_populates="emo_scores")
