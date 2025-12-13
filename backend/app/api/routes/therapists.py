from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from typing import List
from app.services.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.therapist import Therapist
from app.schemas.therapist import TherapistRead, TherapistUpdate, TherapistListItem

router = APIRouter(prefix="/therapists", tags=["therapists"])


@router.get("", response_model=List[TherapistListItem])
def get_all_therapists(
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """
    Get all therapists list.

    This endpoint returns a simplified list of all therapists
    for selection purposes (e.g., in a dropdown).

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        List of TherapistListItem with id, name, age, info
    """
    therapists = db.query(Therapist).all()
    return therapists


@router.get("/{therapist_id}", response_model=TherapistRead)
def get_therapist(
    therapist_id: str,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """
    Get therapist information by ID.

    This endpoint returns complete information about a specific therapist,
    including their prompt template.

    Args:
        therapist_id: The therapist's ID
        current_user: Authenticated user
        db: Database session

    Returns:
        TherapistRead with all therapist information

    Raises:
        HTTPException 404: If therapist not found
    """
    therapist = db.query(Therapist).filter(Therapist.id == therapist_id).first()

    if not therapist:
        raise HTTPException(status_code=404, detail="Therapist not found")

    return therapist


@router.patch("/{therapist_id}", response_model=TherapistRead)
def update_therapist(
    therapist_id: str,
    therapist_update: TherapistUpdate,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """
    Update therapist information.

    This endpoint allows updating any combination of therapist fields:
    name, age, info, and prompt. Only provided fields will be updated.

    Args:
        therapist_id: The therapist's ID
        therapist_update: Fields to update (all optional)
        current_user: Authenticated user
        db: Database session

    Returns:
        TherapistRead with updated therapist information

    Raises:
        HTTPException 404: If therapist not found
    """
    therapist = db.query(Therapist).filter(Therapist.id == therapist_id).first()

    if not therapist:
        raise HTTPException(status_code=404, detail="Therapist not found")

    # Update only provided fields
    update_data = therapist_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(therapist, field, value)

    db.commit()
    db.refresh(therapist)

    return therapist
