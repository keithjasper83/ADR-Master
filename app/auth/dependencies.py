"""Authentication dependencies for FastAPI."""
from typing import Optional

from fastapi import Cookie, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.auth.utils import decode_access_token
from app.db.database import get_db
from app.models.base import User


async def get_current_user(
    authorization: Optional[str] = Header(None),
    adr_session: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user from token or session cookie."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = None
    
    # Try to get token from Authorization header
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
    # Try to get token from session cookie
    elif adr_session:
        token = adr_session
    
    if not token:
        raise credentials_exception
    
    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception
    
    return user


async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    adr_session: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get current user if authenticated, None otherwise."""
    try:
        return await get_current_user(authorization, adr_session, db)
    except HTTPException:
        return None


async def get_user_from_api_key(
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get user from API key header."""
    if not x_api_key:
        return None
    
    user = db.query(User).filter(User.api_key == x_api_key, User.is_active == True).first()
    return user
