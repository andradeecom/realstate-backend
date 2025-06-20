from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr, ConfigDict, field_serializer
from enum import Enum
from .public_user import Token

class UserRole(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    EMPLOYEE = "employee"
    CLIENT = "client"

class TenantUser(SQLModel, table=True):
    __tablename__ = "tenant_user"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(unique=True, min_length=3, max_length=50)
    fullname: str = Field(nullable=True, min_length=3, max_length=50)
    email: EmailStr = Field(nullable=False, unique=True, min_length=5, max_length=100)
    password_hash: str = Field(nullable=False)
    role: UserRole = Field(default=UserRole.CLIENT)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # One-to-one relationship with Token
    token: Optional["Token"] = Relationship(back_populates="tenant_user", sa_relationship_kwargs={"uselist": False})
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()

