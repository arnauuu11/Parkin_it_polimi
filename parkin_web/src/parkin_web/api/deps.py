# src/parkin_web/api/deps.py
from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from src.parkin_web import crud, models, schemas
from src.parkin_web.core import security
from src.parkin_web.core.config import settings
from src.parkin_web.db.session import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")


def get_db() -> Generator:
    """
    Get database session.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> models.User:
    """
    Get current user from token.
    
    Args:
        db: Database session
        token: JWT token
        
    Returns:
        User instance
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Get current active user.
    
    Args:
        current_user: Current user
        
    Returns:
        User instance
        
    Raises:
        HTTPException: If user is not active
    """
    if not crud.user.is_active(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


def get_current_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Get current superuser.
    
    Args:
        current_user: Current user
        
    Returns:
        User instance
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user