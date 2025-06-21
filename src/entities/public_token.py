from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import ConfigDict, field_serializer

class Token(SQLModel, table=True):
    __tablename__ = "token"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    
    # One-to-one relationship with Users
    public_user_id: Optional[UUID] = Field(foreign_key="public_user.id", unique=True)
    public_user: Optional["PublicUser"] = Relationship(back_populates="token", sa_relationship_kwargs={"uselist": False})

    tenant_user_id: Optional[UUID] = Field(foreign_key="tenant_user.id", unique=True)
    tenant_user: Optional["TenantUser"] = Relationship(back_populates="token", sa_relationship_kwargs={"uselist": False})
    
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