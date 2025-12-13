from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func
from typing import List
from app.services.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.session import Session
from app.models.user_context import UserContext
from app.models.therapist import Therapist
from app.schemas.user import UserOverview, UserRead, UserUpdate
from app.schemas.user_context import UserContextResponse
from app.schemas.user_memory import UserMemoryItem
from app.agents.therapist_agent_service import TherapistAgentService

router = APIRouter(prefix="/me", tags=["users"])


@router.get("/overview", response_model=UserOverview)
def get_user_overview(
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """
    Get user overview information for the homepage.

    This endpoint returns:
    - User email
    - Onboarding completion status
    - Total number of sessions
    - Last session time (if any)
    - Next plan (placeholder for future feature)

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        UserOverview with user stats and information
    """
    # Get total sessions count
    total_sessions = db.query(func.count(Session.id)).filter(
        Session.user_id == current_user.id
    ).scalar() or 0

    # Get last session time
    last_session = db.query(Session.start_time).filter(
        Session.user_id == current_user.id
    ).order_by(Session.start_time.desc()).first()

    last_session_time = last_session[0] if last_session else None

    return UserOverview(
        email=current_user.email,
        nickname=current_user.nickname,
        therapist_id=current_user.therapist_id,
        has_finished_onboarding=current_user.has_finished_onboarding,
        is_admin=current_user.is_admin,
        total_sessions=total_sessions,
        last_session_time=last_session_time,
        next_plan=None
    )


@router.get("/context", response_model=UserContextResponse)
def get_user_context(
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """
    Get user context information (Markdown format).

    This endpoint returns the user's context generated from onboarding
    and updated during counseling sessions.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        UserContextResponse with context text and timestamps

    Raises:
        HTTPException: 404 if user context not found
    """
    context = db.query(UserContext).filter_by(user_id=current_user.id).first()

    if not context:
        raise HTTPException(status_code=404, detail="User context not found")

    return UserContextResponse(
        context_text=context.context_text,
        created_at=context.created_at,
        updated_at=context.updated_at
    )


@router.get("/memories", response_model=List[UserMemoryItem])
def get_user_memories(
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """
    Get user's all memories from Agno framework (replacing personas).

    This endpoint retrieves memories automatically extracted by the
    TherapistAgent during conversations. Memories include user facts,
    preferences, and important information.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        List of UserMemoryItem objects with all memory fields:
        - memory_id: Unique identifier
        - memory: Memory content
        - topics: List of related topics
        - created_at: When memory was created
        - updated_at: When memory was last updated

    Raises:
        HTTPException 500: If fetching memories fails
    """
    try:
        therapist_service = TherapistAgentService()
        memories = therapist_service.get_user_memories(user_id=current_user.id)

        return [
            UserMemoryItem(
                memory_id=m["memory_id"],
                memory=m["memory"],
                topics=m["topics"],
                created_at=m["created_at"],
                updated_at=m["updated_at"]
            )
            for m in memories
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch memories: {str(e)}"
        )


@router.patch("", response_model=UserRead)
def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """
    Update user profile information.

    This endpoint allows users to update their profile settings:
    - nickname: User's display name
    - therapist_id: Selected therapist ID

    Args:
        user_update: Fields to update (all optional)
        current_user: Authenticated user
        db: Database session

    Returns:
        UserRead with updated user information

    Raises:
        HTTPException 400: If therapist_id is invalid
    """
    # Validate therapist_id if provided
    if user_update.therapist_id is not None:
        therapist = db.query(Therapist).filter(
            Therapist.id == user_update.therapist_id
        ).first()
        if not therapist:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid therapist_id: {user_update.therapist_id}"
            )

    # Update only provided fields
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return current_user
