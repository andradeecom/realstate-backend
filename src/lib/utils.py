import re
from uuid import UUID
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from src.entities.user import UserRole
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "secret")
ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str):
    """Hash password"""
    return crypt_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str):
    """Verify password against hashed password"""
    return crypt_context.verify(plain_password, hashed_password)

def validate_email(email: str) -> bool:
    """Validate email format"""
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        return False
    return True

def validate_password(password: str) -> bool:
    """Validate password meets security requirements:
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 number
    - At least 1 special character
    """
    if len(password) < 8:
        return False
        
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False
        
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False
        
    # Check for at least one number
    if not re.search(r'[0-9]', password):
        return False
        
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
        
    return True

def validate_role(role: str) -> bool:
    """Validate role format"""
    if role not in UserRole:
        return False
    return True

def generate_auth_token(user_id: UUID, token_type: str, expires_delta: timedelta | None = None) -> str:
    """
    Create JWT token

    Args:
        user_id (UUID): User ID
        token_type (str): Token type
        expires_delta (timedelta | None, optional): Expiration time delta. Defaults to None.
    Returns:
        str: JWT token
    """
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(user_id),     # Using sub claim as per JWT standards
        "exp": int(expire.timestamp()),
        "type": token_type
    }
    return jwt.encode(to_encode, SECRET_KEY, ALGORITHM)


def verify_auth_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode JWT token
    
    Args:
        token (str): JWT token
        
    Returns:
        Dict[str, Any]: Token payload
        
    Raises:
        jwt.PyJWTError: If token is invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        # Let the caller handle the exception
        raise
