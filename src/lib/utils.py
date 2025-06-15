import os
import re
from uuid import UUID
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from src.entities.user import UserRole
load_dotenv()

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

def create_token(user_id: UUID, token_type: str, expires_delta: timedelta | None = None) -> str:
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
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    jwt_secret = os.getenv("JWT_SECRET_KEY")
    jwt_algorithm = os.getenv("JWT_ALGORITHM")
    
    to_encode = {
        "user_id": str(user_id),
        "exp": int(expire.timestamp()),
        "type": token_type
    }
    return jwt.encode(to_encode, jwt_secret, jwt_algorithm)
