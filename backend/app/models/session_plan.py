from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.services.database import Base


class SessionPlan(Base):
    __tablename__ = "session_plans"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    plan_text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    session = relationship("Session", back_populates="plan")
