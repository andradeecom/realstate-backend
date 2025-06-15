from uuid import UUID
from pydantic import BaseModel, EmailStr
from typing import Optional
from src.entities.user import UserRole

class CreateUserRequest(BaseModel):
    username: Optional[str]
    email: EmailStr
    password: str
    role: UserRole = UserRole.CLIENT

class CreateUserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: UserRole
    message: str
    status_code: int

class UpdateUserRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UpdateUserResponse(BaseModel):
    id: UUID
    username: Optional[str]
    email: EmailStr
    role: UserRole
    is_active: bool
    message: str
