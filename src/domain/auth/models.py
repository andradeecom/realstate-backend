from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from src.entities.user import UserRole

class SignupRequest(BaseModel):
    username: Optional[str]
    email: EmailStr
    password: str
    role: UserRole = UserRole.CLIENT

class SignupResponse(BaseModel):
    user_id: UUID
    token: str
class SigninRequest(BaseModel):
    email: EmailStr
    password: str

class SigninResponse(BaseModel):
    user_id: UUID
    access_token: str
    refresh_token: str
    message: str

class SignoutRequest(BaseModel):
    token: str
    
class SignoutResponse(BaseModel):
    message: str
