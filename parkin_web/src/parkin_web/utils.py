# src/parkin_web/utils.py
import jwt
from typing import Optional
from datetime import datetime, timedelta

from src.parkin_web.core.config import settings


def generate_password_reset_token(email: str) -> str:
    """
    Generate a JWT token for password reset.
    
    Args:
        email: Email of the user
        
    Returns:
        JWT token as string
    """
    delta = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_MINUTES / 60)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email}, settings.SECRET_KEY, algorithm="HS256",
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token.
    
    Args:
        token: JWT token to verify
        
    Returns:
        Email from token if valid, None otherwise
    """
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return decoded_token["sub"]
    except jwt.JWTError:
        return None


def generate_security_access_code() -> str:
    """
    Generate a random security access code for parking spaces.
    
    Returns:
        Random 6-digit code as string
    """
    import random
    return ''.join(random.choices('0123456789', k=6))