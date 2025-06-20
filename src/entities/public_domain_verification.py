from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Dict, Any, Annotated
from sqlmodel import SQLModel, Field, Relationship
from pydantic import  ConfigDict, field_serializer
from enum import Enum


class Status(SQLModel, Enum):
    PENDING = "pending"
    VERIFIED = "verified"

class DomainVerification(SQLModel, table=True):
    __tablename__ = "domain_verification"
    from src.entities import public_tenant

    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    domain: str = Field(nullable=False)
    status: Status = Field(nullable=False)
    custom_domain: str = Field(nullable=False)
    verification_token: str = Field(nullable=False)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    tenant_id: UUID = Field(nullable=False, foreign_key="tenant.id")

    # One-to-one relationship with Token
    tenant: Optional[public_tenant.Tenant] = Relationship(back_populates="tenant", sa_relationship_kwargs={"uselist": False})
    
    # formatting the datetime fields
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()

