from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Dict, Any, Annotated
from sqlmodel import SQLModel, Field, Relationship
from pydantic import  ConfigDict, field_serializer


class Tenant(SQLModel, table=True):
    __tablename__ = "tenant"
    
    from src.entities import public_plan
    from src.entities import public_stripe_account


    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(min_length=3, max_length=50)
    schema_name: str = Field(min_length=3, max_length=50)
    custom_domain: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Foreign key to Plan
    plan_id: UUID = Field(nullable=False, foreign_key="plan.id")

    # One-to-many relationship with Token
    plan: Optional[public_plan.Plan] = Relationship(back_populates="tenant")
    # One-to-one relationship with StripeAccount
    stripe_account: Optional[public_stripe_account.StripeAccount] = Relationship(back_populates="tenant", sa_relationship_kwargs={"uselist": False})
    
    # formatting the datetime fields
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()

