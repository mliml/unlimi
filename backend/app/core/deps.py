"""
Dependency functions for FastAPI routes.
These can be used with Depends() to add authentication and authorization to endpoints.
"""
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.core.security import decode_access_token
from app.services.user_service import UserService

security = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.

    This function:
    1. Extracts the JWT token from the Authorization header
    2. Decodes and validates the token
    3. Retrieves the user from the database
    4. Returns the user object

    Usage in routes:
        @router.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"message": f"Hello {current_user.email}"}

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        User object of the authenticated user

    Raises:
        HTTPException 401: If token is invalid or user not found
    """
    token = credentials.credentials

    # Decode token
    email = decode_access_token(token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user = UserService.get_user_by_email(db, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependency to get the current active user.

    This is a placeholder for future user status checks.
    You can add additional checks here like:
    - User email verification status
    - User account suspension status
    - User subscription status

    Args:
        current_user: User object from get_current_user

    Returns:
        User object if active

    Raises:
        HTTPException 400: If user is inactive
    """
    # Add your active user checks here if needed
    # Example:
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")

    return current_user


def get_current_admin(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependency to verify that the current user is an admin.

    Usage:
        @router.get("/admin-only")
        def admin_route(admin: User = Depends(get_current_admin)):
            return {"message": "Admin access granted"}

    Args:
        current_user: Current authenticated user

    Returns:
        User object if user is admin

    Raises:
        HTTPException 403: If user is not an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
