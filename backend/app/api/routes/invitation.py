"""
Invitation Code Routes

API endpoints for invitation code management (Admin only).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.deps import get_current_admin
from app.db.models.user import User
from app.db.models.invitation_code import InvitationCode
from app.schemas.invitation import InvitationCodeResponse, InvitationCodeListResponse
from app.services.invitation_service import InvitationService

router = APIRouter(prefix="/admin/invitation-codes", tags=["admin", "invitation"])


@router.post("", response_model=InvitationCodeResponse, status_code=status.HTTP_201_CREATED)
def create_invitation_code(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Create a new invitation code (Admin only).

    Returns:
        Created invitation code
    """
    try:
        invitation = InvitationService.create_invitation_code(db)

        return InvitationCodeResponse(
            id=invitation.id,
            code=invitation.code,
            is_universal=invitation.is_universal,
            is_used=invitation.is_used,
            used_by_email=None,
            used_at=None,
            created_at=invitation.created_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create invitation code: {str(e)}"
        )


@router.get("", response_model=InvitationCodeListResponse)
def get_invitation_codes(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Get all invitation codes (Admin only).

    Returns:
        List of all invitation codes with usage information
    """
    try:
        codes = InvitationService.get_all_codes(db)

        code_responses = []
        for code in codes:
            used_by_email = None
            if code.used_by_user_id:
                user = db.query(User).filter(User.id == code.used_by_user_id).first()
                used_by_email = user.email if user else None

            code_responses.append(InvitationCodeResponse(
                id=code.id,
                code=code.code,
                is_universal=code.is_universal,
                is_used=code.is_used,
                used_by_email=used_by_email,
                used_at=code.used_at,
                created_at=code.created_at
            ))

        return InvitationCodeListResponse(codes=code_responses)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get invitation codes: {str(e)}"
        )


@router.delete("/{code_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invitation_code(
    code_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Delete an unused invitation code (Admin only).

    Args:
        code_id: ID of the invitation code to delete

    Raises:
        HTTPException 400: If code is used or universal
        HTTPException 404: If code not found
    """
    invitation = db.query(InvitationCode).filter(InvitationCode.id == code_id).first()

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation code not found"
        )

    if invitation.is_universal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete universal invitation code"
        )

    if invitation.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete used invitation code"
        )

    success = InvitationService.delete_code(db, code_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete invitation code"
        )
