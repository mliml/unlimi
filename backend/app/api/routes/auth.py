from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserPublic
from app.schemas.auth import TokenResponse
from app.services.user_service import UserService
from app.services.captcha_service import CaptchaService
from app.services.invitation_service import InvitationService
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user with captcha and invitation code verification.

    This endpoint:
    1. Verifies the captcha
    2. Verifies the invitation code
    3. Checks if the email is already registered
    4. Creates a new user with hashed password
    5. Marks the invitation code as used
    6. Generates a JWT access token
    7. Returns the token and user information

    Args:
        user_data: User registration data (email, password, invitation_code, captcha)
        db: Database session

    Returns:
        TokenResponse containing access_token and user information

    Raises:
        HTTPException 400: If captcha/invitation code is invalid or email is already registered
        HTTPException 422: If validation fails
    """
    # 1. Verify captcha
    if not CaptchaService.verify_captcha(db, user_data.captcha_session_id, user_data.captcha_text):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired captcha"
        )

    # 2. Verify invitation code
    if not InvitationService.verify_invitation_code(db, user_data.invitation_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or used invitation code"
        )

    # 3. Check if user already exists
    if UserService.user_exists(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    try:
        # 4. Create new user
        user = UserService.create_user(db, user_data)

        # 5. Mark invitation code as used
        InvitationService.use_invitation_code(db, user_data.invitation_code, user.id)

        # 6. Generate access token
        access_token = create_access_token(subject=user.email)

        # 7. Convert user to public schema
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
    Authenticate a user and return access token with captcha verification.

    This endpoint:
    1. Verifies the captcha
    2. Validates user credentials (email and password)
    3. Generates a JWT access token if credentials are valid
    4. Returns the token and user information

    Args:
        user_credentials: User login credentials (email, password, captcha)
        db: Database session

    Returns:
        TokenResponse containing access_token and user information

    Raises:
        HTTPException 400: If captcha is invalid
        HTTPException 401: If credentials are invalid
    """
    # 1. Verify captcha
    if not CaptchaService.verify_captcha(db, user_credentials.captcha_session_id, user_credentials.captcha_text):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired captcha"
        )

    # 2. Authenticate user
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

    # 3. Generate access token
    access_token = create_access_token(subject=user.email)

    # 4. Convert user to public schema
    user_public = UserPublic.model_validate(user)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_public
    )
