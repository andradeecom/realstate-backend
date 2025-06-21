from uuid import UUID, uuid4
from datetime import datetime
from typing import List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr, ConfigDict, field_serializer

class Client(SQLModel, table=True):
    __tablename__ = "client"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    fullname: str = Field(nullable=True, min_length=3, max_length=50)
    email: EmailStr = Field(nullable=False, unique=True, min_length=5, max_length=100)
    phone: str = Field(nullable=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Foreign key reference to tenant_user without relationship object
    user_id: UUID = Field(nullable=False, foreign_key="tenant_user.id")

    reservations: List["Reservation"] = Relationship(back_populates="client")
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()
