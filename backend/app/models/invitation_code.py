"""
InvitationCode Model

Manages invitation codes for user registration.
Supports both single-use codes and universal codes.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.services.database import Base


class InvitationCode(Base):
    """
    Invitation code model for registration management.

    Attributes:
        id: Primary key
        code: Unique invitation code string (8 chars for regular, custom for universal)
        is_universal: Whether this is a universal (unlimited use) code
        is_used: Whether this code has been used (only for non-universal codes)
        used_by_user_id: User ID who used this code (NULL if unused or universal)
        used_at: Timestamp when code was used
        created_at: Timestamp when code was created
    """
    __tablename__ = "invitation_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    is_universal = Column(Boolean, default=False, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False, index=True)
    used_by_user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    used_by = relationship("User", foreign_keys=[used_by_user_id], backref="invitation_used")
