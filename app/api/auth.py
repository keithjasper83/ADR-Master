"""Authentication API endpoints."""
import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.utils import (
    create_access_token,
    generate_api_key,
    get_password_hash,
    verify_password,
)
from app.config import get_settings
from app.db.database import get_db
from app.models.base import User

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


class RegisterRequest(BaseModel):
    """User registration request."""

    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """Login request."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response."""

    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    """User response."""

    id: int
    email: str
    is_active: bool
    has_api_key: bool

    class Config:
        from_attributes = True


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    hashed_password = get_password_hash(request.password)
    user = User(
        email=request.email,
        hashed_password=hashed_password,
        is_active=True,
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    # Set session cookie
    response.set_cookie(
        key=settings.session_cookie_name,
        value=access_token,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite=settings.session_cookie_samesite,
        max_age=settings.jwt_expiration_hours * 3600,
    )
    
    return TokenResponse(
        access_token=access_token,
        user={"id": user.id, "email": user.email, "is_active": user.is_active},
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Login user."""
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    # Set session cookie
    response.set_cookie(
        key=settings.session_cookie_name,
        value=access_token,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite=settings.session_cookie_samesite,
        max_age=settings.jwt_expiration_hours * 3600,
    )
    
    return TokenResponse(
        access_token=access_token,
        user={"id": user.id, "email": user.email, "is_active": user.is_active},
    )


@router.post("/logout")
async def logout(response: Response):
    """Logout user."""
    response.delete_cookie(key=settings.session_cookie_name)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        is_active=current_user.is_active,
        has_api_key=current_user.api_key is not None,
    )


@router.post("/api-key/generate")
async def generate_user_api_key(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Generate a new API key for the current user."""
    api_key = generate_api_key()
    current_user.api_key = api_key
    db.commit()
    
    return {"api_key": api_key, "message": "API key generated. Store it securely!"}


@router.delete("/api-key/revoke")
async def revoke_api_key(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Revoke the current user's API key."""
    current_user.api_key = None
    db.commit()
    
    return {"message": "API key revoked"}
