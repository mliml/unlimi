from sqlalchemy.orm import Session
from typing import Optional
from app.db.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password


class UserService:
    """Service class for user-related operations."""

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Retrieve a user by email address.

        Args:
            db: Database session
            email: User's email address

        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Retrieve a user by ID.

        Args:
            db: Database session
            user_id: User's ID

        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> User:
        """
        Create a new user with hashed password.

        Args:
            db: Database session
            user_create: User creation data

        Returns:
            Newly created User object
        """
        hashed_password = hash_password(user_create.password)
        db_user = User(
            email=user_create.email,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.

        Args:
            db: Database session
            email: User's email address
            password: Plain text password to verify

        Returns:
            User object if authentication succeeds, None otherwise
        """
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def user_exists(db: Session, email: str) -> bool:
        """
        Check if a user with given email exists.

        Args:
            db: Database session
            email: Email address to check

        Returns:
            True if user exists, False otherwise
        """
        return db.query(User).filter(User.email == email).first() is not None
