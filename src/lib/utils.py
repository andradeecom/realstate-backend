import os
import re
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from src.entities.user import UserRole
load_dotenv()

def hash_password(password: str):
    """Hash password using bcrypt"""
    # Maybe we can change this later to use passlib -> pip install "passlib[bcrypt]"
    salt = bcrypt.gensalt(12)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(password: str, hashed_password: str):
    """Verify password against hashed password"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

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

def create_access_token(user_id: str) -> str:
    """Create access token with expiration (If not provided in .env, default to 15 minutes)"""
    jwt_secret = os.getenv("JWT_SECRET_KEY")
    access_token_expire = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=access_token_expire)
    to_encode = {
        "user_id": user_id,
        "exp": int(expire.timestamp()),
        "type": "access"
    }
    return jwt.encode(to_encode, jwt_secret, algorithm="HS256")

def create_refresh_token(user_id: str) -> str:
    """Create refresh token with expiration (If not provided in .env, default to 7 days)"""
    jwt_secret = os.getenv("JWT_REFRESH_SECRET_KEY")
    refresh_token_expire = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    expire = datetime.now(timezone.utc) + timedelta(days=refresh_token_expire)
    to_encode = {
        "user_id": user_id,
        "exp": int(expire.timestamp()),
        "type": "refresh"
    }
    return jwt.encode(to_encode, jwt_secret, algorithm="HS256")