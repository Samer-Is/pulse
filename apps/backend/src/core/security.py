"""
Security utilities: JWT tokens, password hashing, etc.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from passlib.context import CryptContext

from .config import get_settings
from .logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Payload data (typically {'sub': user_id})
        expires_delta: Token expiration time (default: from settings)
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode error: {str(e)}")
        return None


def create_magic_link_token(email: str) -> str:
    """
    Create short-lived token for magic link authentication.
    
    Args:
        email: User email address
    
    Returns:
        JWT token (10 minute expiry)
    """
    expires_delta = timedelta(minutes=10)
    data = {
        "sub": email,
        "type": "magic_link"
    }
    return create_access_token(data, expires_delta)


def verify_magic_link_token(token: str) -> Optional[str]:
    """
    Verify magic link token and extract email.
    
    Args:
        token: Magic link JWT token
    
    Returns:
        Email address or None if invalid
    """
    payload = decode_access_token(token)
    
    if not payload:
        return None
    
    if payload.get("type") != "magic_link":
        logger.warning("Token is not a magic link token")
        return None
    
    email = payload.get("sub")
    return email


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


def generate_csrf_token() -> str:
    """Generate CSRF token for forms."""
    from secrets import token_urlsafe
    return token_urlsafe(32)
