from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import ConfigDict, field_serializer
from enum import Enum

class Status(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"

class DomainVerification(SQLModel, table=True):
    __tablename__ = "domain_verification"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    domain: str = Field(nullable=False)
    status: Status = Field(nullable=False)
    custom_domain: str = Field(nullable=False)
    verification_token: str = Field(nullable=False)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # One-to-one relationship with Tenant using string-based forward reference
    tenant_id: Optional[UUID] = Field(foreign_key="tenant.id", unique=True)
    tenant: Optional["Tenant"] = Relationship(back_populates="domain_verification", sa_relationship_kwargs={"uselist": False})
    
    # formatting the datetime fields
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()

