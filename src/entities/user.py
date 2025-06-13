from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Dict, Any, Annotated, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr, ConfigDict, field_serializer
from enum import Enum

class UserRole(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    CLIENT = "client"

class User(SQLModel, table=True):
    __tablename__ = "user"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(unique=True, min_length=3, max_length=50)
    email: EmailStr = Field(nullable=False, unique=True, min_length=5, max_length=100)
    password_hash: str = Field(nullable=False)
    role: UserRole = Field(default=UserRole.CLIENT)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # One-to-one relationship with Token
    token: Optional["Token"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})
    properties: List["Property"] = Relationship(back_populates="owner")
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()
    
class Property(SQLModel, table=True):
    __tablename__ = "property"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    address: str = Field(unique=True, min_length=10, max_length=50)
    title:str = Field(nullable=False, min_length=5, max_length=30)
    cover_image: str = Field(default=None) # name of file ? That's how I had it in the old version
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # one to many relationship with user (can have several properties)
    owner_id: UUID = Field(foreign_key="user.id") 
    owner: User = Relationship(back_populates="properties")

    # relationship to reservations table
    # relationship to costs table

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
    token_type: str = "bearer"
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    
    # One-to-one relationship with User
    user_id: UUID = Field(foreign_key="user.id", unique=True)
    user: "User" = Relationship(back_populates="token")
    
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
    token_type: str = "bearer"
    expires_at: datetime
    
    model_config = ConfigDict()
    
    @field_serializer('expires_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()