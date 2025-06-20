from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import  ConfigDict, field_serializer

class Plan(SQLModel, table=True):
    __tablename__ = "plan"
    from src.entities import public_tenant
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(min_length=3, max_length=50)
    max_users: int = Field(nullable=False)
    max_property: int = Field(nullable=False)
    price_per_month: int = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Foreign key to Tenant
    tenants: list[UUID] = Field(nullable=False, foreign_key="tenant.id")

    # Many-to-one relationship with Token
    tenant: Optional[public_tenant.Tenant] = Relationship(back_populates="plan")
    
    # formatting the datetime fields
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()

