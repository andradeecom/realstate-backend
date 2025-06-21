from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import ConfigDict, field_serializer

class Tenant(SQLModel, table=True):
    __tablename__ = "tenant"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(min_length=3, max_length=50)
    schema_name: str = Field(min_length=3, max_length=50)
    custom_domain: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Foreign key to Plan
    plan_id: UUID = Field(nullable=False, foreign_key="plan.id")

    # One-to-many relationship with Plan using string-based forward reference
    plan: Optional["Plan"] = Relationship(back_populates="tenants")
    # One-to-one relationship with StripeAccount using string-based forward reference
    stripe_account: Optional["StripeAccount"] = Relationship(back_populates="tenant", sa_relationship_kwargs={"uselist": False})
    # One-to-one relationship with DomainVerification using string-based forward reference
    domain_verification: Optional["DomainVerification"] = Relationship(back_populates="tenant", sa_relationship_kwargs={"uselist": False})
    
    # formatting the datetime fields
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()

