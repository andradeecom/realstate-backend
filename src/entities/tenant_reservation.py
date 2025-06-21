from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from pydantic import ConfigDict, field_serializer
from enum import Enum

class Status(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Reservation(SQLModel, table=True):
    __tablename__ = "reservation"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    start_date: datetime = Field(nullable=False)
    end_date: datetime = Field(nullable=False)
    status: Status = Field(default=Status.PENDING)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    property_id: UUID = Field(nullable=False, foreign_key="property.id")
    property: "Property" = Relationship(back_populates="reservations")
    client_id: UUID = Field(nullable=False, foreign_key="client.id")
    client: "Client" = Relationship(back_populates="reservations")

    agent_id: UUID = Field(nullable=False, foreign_key="tenant_user.id")

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()
