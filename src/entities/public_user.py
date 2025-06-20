from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Dict, Any, Annotated
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr, ConfigDict, field_serializer
from enum import Enum

class UserRole(str, Enum):
    SUPERADMIN = "superadmin"
    SUPPORT = "support"

class PublicUser(SQLModel, table=True):
    __tablename__ = "public_user"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(unique=True, min_length=3, max_length=50)
    fullname: str = Field(nullable=True, min_length=3, max_length=50)
    email: EmailStr = Field(nullable=False, unique=True, min_length=5, max_length=100)
    password_hash: str = Field(nullable=False)
    role: UserRole = Field(default=UserRole.SUPERADMIN)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # One-to-one relationship with Token
    token: Optional["Token"] = Relationship(back_populates="public_user", sa_relationship_kwargs={"uselist": False}) # the sa_relationship ... makes it a one to one
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()

class Token(SQLModel, table=True):
    __tablename__ = "token"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    
    # One-to-one relationship with User
    user_id: UUID = Field(foreign_key="user.id", unique=True)
    user: "PublicUser" = Relationship(back_populates="token")
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    
    @field_serializer('expires_at', 'created_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()

# Simple DTO for token responses
class TokenResponse(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_at: datetime
    
    model_config = ConfigDict()
    
    @field_serializer('expires_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()