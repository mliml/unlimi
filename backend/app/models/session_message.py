from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.services.database import Base


class MessageSender(str, enum.Enum):
    user = "user"
    therapist = "therapist"
    system = "system"


class SessionMessage(Base):
    __tablename__ = "session_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    sender = Column(SQLEnum(MessageSender), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    session = relationship("Session", back_populates="messages")
