from pydantic import BaseModel
from app.schemas.user import UserPublic


class TokenResponse(BaseModel):
    """Response model for authentication endpoints."""
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class TokenData(BaseModel):
    """Data extracted from JWT token."""
    email: str | None = None
