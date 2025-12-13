"""
Invitation Service

Handles invitation code generation, verification, and management.
"""

import random
import string
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List

from app.models.invitation_code import InvitationCode


class InvitationService:
    """Service for managing invitation codes."""

    CODE_LENGTH = 8
    UNIVERSAL_CODE = "WuSY_940315"

    @staticmethod
    def generate_code() -> str:
        """Generate a random 8-character invitation code (digits + uppercase letters)."""
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choices(chars, k=InvitationService.CODE_LENGTH))

    @staticmethod
    def create_invitation_code(db: Session) -> InvitationCode:
        """
        Create a new invitation code.

        Args:
            db: Database session

        Returns:
            Created InvitationCode object
        """
        # Generate unique code
        while True:
            code = InvitationService.generate_code()
            existing = db.query(InvitationCode).filter(InvitationCode.code == code).first()
            if not existing:
                break

        invitation = InvitationCode(
            code=code,
            is_universal=False,
            is_used=False
        )
        db.add(invitation)
        db.commit()
        db.refresh(invitation)

        return invitation

    @staticmethod
    def verify_invitation_code(db: Session, code: str) -> bool:
        """
        Verify if an invitation code is valid and available.

        Args:
            db: Database session
            code: Invitation code to verify

        Returns:
            True if code is valid and available, False otherwise
        """
        invitation = db.query(InvitationCode).filter(InvitationCode.code == code).first()

        if not invitation:
            return False

        # Universal code is always valid
        if invitation.is_universal:
            return True

        # Regular code must be unused
        return not invitation.is_used

    @staticmethod
    def use_invitation_code(db: Session, code: str, user_id: int) -> bool:
        """
        Mark an invitation code as used.

        Args:
            db: Database session
            code: Invitation code
            user_id: ID of user who used the code

        Returns:
            True if successful, False otherwise
        """
        invitation = db.query(InvitationCode).filter(InvitationCode.code == code).first()

        if not invitation:
            return False

        # Don't modify universal codes
        if invitation.is_universal:
            return True

        # Don't allow already-used codes
        if invitation.is_used:
            return False

        # Mark as used
        invitation.is_used = True
        invitation.used_by_user_id = user_id
        invitation.used_at = datetime.utcnow()
        db.commit()

        return True

    @staticmethod
    def get_all_codes(db: Session) -> List[InvitationCode]:
        """Get all invitation codes with user information."""
        return db.query(InvitationCode).order_by(InvitationCode.created_at.desc()).all()

    @staticmethod
    def delete_code(db: Session, code_id: int) -> bool:
        """
        Delete an unused invitation code.

        Args:
            db: Database session
            code_id: ID of code to delete

        Returns:
            True if deleted, False if code is used or universal
        """
        invitation = db.query(InvitationCode).filter(InvitationCode.id == code_id).first()

        if not invitation:
            return False

        # Cannot delete universal code
        if invitation.is_universal:
            return False

        # Cannot delete used code
        if invitation.is_used:
            return False

        db.delete(invitation)
        db.commit()
        return True
