"""
CaptchaSession Model

Manages captcha verification sessions.
Stores captcha text and expiration for one-time verification.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.services.database import Base


class CaptchaSession(Base):
    """
    Captcha session model for verification management.

    Attributes:
        id: Primary key
        session_id: Unique session identifier (UUID from frontend)
        captcha_text: The correct captcha answer (4 digits)
        created_at: Timestamp when session was created
        expires_at: Timestamp when session expires (5 minutes after creation)
    """
    __tablename__ = "captcha_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), unique=True, nullable=False, index=True)
    captcha_text = Column(String(4), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)
