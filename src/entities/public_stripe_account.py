from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import  ConfigDict, field_serializer
from enum import Enum
class Mode(str, Enum):
    LIVE = "live"
    TEST = "test"
class StripeAccount(SQLModel, table=True):
    __tablename__ = "stripe_account"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    stripe_account_id: str = Field(nullable=False)
    model: Mode = Field(default=Mode.TEST)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    tenant_id: UUID = Field(nullable=False, foreign_key="tenant.id")

    # One-to-one relationship with Tenant using string-based forward reference
    tenant: Optional["Tenant"] = Relationship(back_populates="stripe_account", sa_relationship_kwargs={"uselist": False})
    
    # formatting the datetime fields
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()

