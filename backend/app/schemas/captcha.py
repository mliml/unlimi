"""
Captcha Schemas

Pydantic models for captcha generation and verification.
"""

from pydantic import BaseModel, Field


class CaptchaResponse(BaseModel):
    """Response for captcha generation."""
    session_id: str
    image_base64: str
    expires_in: int  # seconds


class CaptchaVerifyRequest(BaseModel):
    """Request to verify captcha."""
    session_id: str
    captcha_text: str = Field(..., min_length=4, max_length=4)
