from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserPublic
from app.schemas.auth import TokenResponse
from app.services.user_service import UserService
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.

    This endpoint:
    1. Checks if the email is already registered
    2. Creates a new user with hashed password
    3. Generates a JWT access token
    4. Returns the token and user information

    Args:
        user_data: User registration data (email and password)
        db: Database session

    Returns:
        TokenResponse containing access_token and user information

    Raises:
        HTTPException 400: If email is already registered
        HTTPException 422: If validation fails
    """
    # Check if user already exists
    if UserService.user_exists(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    try:
        # Create new user
        user = UserService.create_user(db, user_data)

        # Generate access token
        access_token = create_access_token(subject=user.email)

        # Convert user to public schema
        user_public = UserPublic.model_validate(user)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_public
        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during registration: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and return access token.

    This endpoint:
    1. Validates user credentials (email and password)
    2. Generates a JWT access token if credentials are valid
    3. Returns the token and user information

    Args:
        user_credentials: User login credentials (email and password)
        db: Database session

    Returns:
        TokenResponse containing access_token and user information

    Raises:
        HTTPException 401: If credentials are invalid
    """
    # Authenticate user
    user = UserService.authenticate_user(
        db,
        user_credentials.email,
        user_credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate access token
    access_token = create_access_token(subject=user.email)

    # Convert user to public schema
    user_public = UserPublic.model_validate(user)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_public
    )
