from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    nickname = Column(String, nullable=True)
    therapist_id = Column(String, ForeignKey('therapists.id'), nullable=False, default='01')
    has_finished_onboarding = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    therapist = relationship("Therapist", back_populates="users")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    onboardings = relationship("UserOnboarding", back_populates="user", cascade="all, delete-orphan")
    context = relationship("UserContext", back_populates="user", uselist=False, cascade="all, delete-orphan")
    emo_scores = relationship("EmoScore", back_populates="user", cascade="all, delete-orphan", order_by="EmoScore.created_at.desc()")
