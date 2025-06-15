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
