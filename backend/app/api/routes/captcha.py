"""
Captcha Routes

API endpoints for captcha generation and verification.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.captcha import CaptchaResponse
from app.services.captcha_service import CaptchaService

router = APIRouter(prefix="/captcha", tags=["captcha"])


@router.get("/generate", response_model=CaptchaResponse)
def generate_captcha(db: Session = Depends(get_db)):
    """
    Generate a new captcha image.

    Returns:
        CaptchaResponse with session_id and base64-encoded image
    """
    try:
        session_id, image_base64, expires_in = CaptchaService.create_captcha_session(db)

        return CaptchaResponse(
            session_id=session_id,
            image_base64=image_base64,
            expires_in=expires_in
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate captcha: {str(e)}"
        )
