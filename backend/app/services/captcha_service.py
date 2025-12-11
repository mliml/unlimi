"""
Captcha Service

Handles captcha generation, image rendering, and verification.
"""

import random
import string
import uuid
from datetime import datetime, timedelta
from io import BytesIO
import base64
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from sqlalchemy.orm import Session
from typing import Tuple

from app.db.models.captcha_session import CaptchaSession


class CaptchaService:
    """Service for generating and verifying captchas."""

    CAPTCHA_LENGTH = 4
    CAPTCHA_EXPIRY_MINUTES = 5
    IMAGE_WIDTH = 160
    IMAGE_HEIGHT = 60

    @staticmethod
    def generate_captcha_text() -> str:
        """Generate random 4-digit captcha text."""
        return ''.join(random.choices(string.digits, k=CaptchaService.CAPTCHA_LENGTH))

    @staticmethod
    def generate_captcha_image(text: str) -> str:
        """
        Generate captcha image and return as base64 string.

        Args:
            text: The captcha text to render

        Returns:
            Base64-encoded PNG image
        """
        # Create image with white background
        image = Image.new('RGB', (CaptchaService.IMAGE_WIDTH, CaptchaService.IMAGE_HEIGHT), 'white')
        draw = ImageDraw.Draw(image)

        # Try to load a font, fallback to default if not available
        try:
            # Try common font paths for macOS and Linux
            for font_path in [
                '/System/Library/Fonts/Supplemental/Arial.ttf',  # macOS
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',  # Linux
                '/Library/Fonts/Arial.ttf',  # macOS alternative
            ]:
                try:
                    font = ImageFont.truetype(font_path, 36)
                    break
                except:
                    continue
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()

        # Draw noise lines
        for _ in range(5):
            x1 = random.randint(0, CaptchaService.IMAGE_WIDTH)
            y1 = random.randint(0, CaptchaService.IMAGE_HEIGHT)
            x2 = random.randint(0, CaptchaService.IMAGE_WIDTH)
            y2 = random.randint(0, CaptchaService.IMAGE_HEIGHT)
            draw.line(
                [(x1, y1), (x2, y2)],
                fill=(random.randint(150, 200), random.randint(150, 200), random.randint(150, 200)),
                width=1
            )

        # Draw captcha text
        # Calculate text positioning
        x_offset = 20
        char_spacing = 30

        # Draw each character with slight offset
        for i, char in enumerate(text):
            offset_x = x_offset + i * char_spacing + random.randint(-3, 3)
            offset_y = 10 + random.randint(-5, 5)
            color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
            draw.text((offset_x, offset_y), char, font=font, fill=color)

        # Add noise points
        for _ in range(100):
            xy = (random.randint(0, CaptchaService.IMAGE_WIDTH), random.randint(0, CaptchaService.IMAGE_HEIGHT))
            draw.point(xy, fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

        # Apply slight blur
        image = image.filter(ImageFilter.SMOOTH)

        # Convert to base64
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return image_base64

    @staticmethod
    def create_captcha_session(db: Session) -> Tuple[str, str, int]:
        """
        Create a new captcha session.

        Args:
            db: Database session

        Returns:
            Tuple of (session_id, image_base64, expires_in_seconds)
        """
        # Clean up expired sessions
        CaptchaService.cleanup_expired_sessions(db)

        # Generate captcha
        session_id = str(uuid.uuid4())
        captcha_text = CaptchaService.generate_captcha_text()
        image_base64 = CaptchaService.generate_captcha_image(captcha_text)

        # Save to database
        expires_at = datetime.utcnow() + timedelta(minutes=CaptchaService.CAPTCHA_EXPIRY_MINUTES)
        captcha_session = CaptchaSession(
            session_id=session_id,
            captcha_text=captcha_text,
            expires_at=expires_at
        )
        db.add(captcha_session)
        db.commit()

        expires_in = CaptchaService.CAPTCHA_EXPIRY_MINUTES * 60
        return session_id, image_base64, expires_in

    @staticmethod
    def verify_captcha(db: Session, session_id: str, user_input: str) -> bool:
        """
        Verify captcha input.

        Args:
            db: Database session
            session_id: Captcha session ID
            user_input: User's captcha input

        Returns:
            True if captcha is valid, False otherwise
        """
        # Find session
        captcha_session = db.query(CaptchaSession).filter(
            CaptchaSession.session_id == session_id
        ).first()

        if not captcha_session:
            return False

        # Check expiry
        if datetime.utcnow() > captcha_session.expires_at:
            db.delete(captcha_session)
            db.commit()
            return False

        # Verify text (case-insensitive)
        is_valid = captcha_session.captcha_text.lower() == user_input.lower()

        # Delete session after verification (one-time use)
        db.delete(captcha_session)
        db.commit()

        return is_valid

    @staticmethod
    def cleanup_expired_sessions(db: Session) -> None:
        """Clean up expired captcha sessions."""
        db.query(CaptchaSession).filter(
            CaptchaSession.expires_at < datetime.utcnow()
        ).delete()
        db.commit()
