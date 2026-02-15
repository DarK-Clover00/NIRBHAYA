"""
Authentication and JWT token management
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.config import settings
from backend.database import get_db
from backend.models.user import User
import hashlib
import uuid

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()


def generate_device_fingerprint() -> str:
    """
    Generate a unique device fingerprint
    Returns a unique identifier for the device
    """
    return str(uuid.uuid4())


def hash_device_fingerprint(fingerprint: str) -> str:
    """
    Hash device fingerprint for storage
    Returns SHA256 hash of the fingerprint
    """
    return hashlib.sha256(fingerprint.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Dictionary containing claims to encode in the token
        expires_delta: Optional expiration time delta
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and verify JWT access token
    
    Args:
        token: JWT token string
    
    Returns:
        Dictionary containing decoded claims
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer credentials containing JWT token
        db: Database session
    
    Returns:
        User object for the authenticated user
    
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    user_id: str = payload.get("sub")
    device_fingerprint: str = payload.get("device_fingerprint")
    
    if user_id is None or device_fingerprint is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Query user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify device fingerprint matches
    if user.device_fingerprint != device_fingerprint:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Device fingerprint mismatch",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is banned or flagged as fraud
    if user.status == "banned" or user.classification == "Fraud":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account access restricted",
        )
    
    return user


def verify_device_fingerprint(user: User, device_fingerprint: str) -> bool:
    """
    Verify that device fingerprint matches user's registered fingerprint
    
    Args:
        user: User object
        device_fingerprint: Device fingerprint to verify
    
    Returns:
        True if fingerprint matches, False otherwise
    """
    return user.device_fingerprint == device_fingerprint
