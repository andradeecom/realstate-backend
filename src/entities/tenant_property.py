from uuid import UUID, uuid4
from datetime import datetime
from typing import List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import ConfigDict, field_serializer
from enum import Enum

class Status(str, Enum):
    AVAILABLE = "available"
    RENTED = "rented"
    SOLD = "sold"

class Property(SQLModel, table=True):
    __tablename__ = "property"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(unique=True, min_length=3, max_length=50)
    description: str = Field(nullable=True, min_length=3, max_length=500)
    price: int = Field(nullable=False) # price in cents
    status: Status = Field(default=Status.AVAILABLE)
    address: str = Field(nullable=False, unique=True, min_length=5, max_length=100)
    listed_at: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    agent_id: UUID = Field(nullable=False, foreign_key="tenant_user.id")

    # Using forward reference to avoid circular imports
    images: List["PropertyImage"] = Relationship(back_populates="property")
    reservations: List["Reservation"] = Relationship(back_populates="property")
    # appointments: List["Appointment"] = Relationship(back_populates="property")
    # contracts: List["Contract"] = Relationship(back_populates="property")
    # client_properties: List["ClientProperty"] = Relationship(back_populates="property")
    # payouts: List["Payout"] = Relationship(back_populates="property")

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()
