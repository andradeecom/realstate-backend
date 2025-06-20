from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from src.entities.tenant_user import UserRole
from src.entities.public_user import TokenResponse

class SignupRequest(BaseModel):
    username: Optional[str]
    email: EmailStr
    password: str
    role: UserRole = UserRole.CLIENT

class SignupResponse(BaseModel):
    user_id: UUID
    token: TokenResponse
    message: str
    
class SigninRequest(BaseModel):
    email: EmailStr
    password: str

class SigninResponse(BaseModel):
    user_id: UUID
    token: TokenResponse
    message: str

class SignoutRequest(BaseModel):
    token: str
    
class SignoutResponse(BaseModel):
    message: str

class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    user_id: UUID
    token: TokenResponse
    message: str
