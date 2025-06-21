from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from pydantic import ConfigDict, field_serializer
from .tenant_property import Property

class PropertyImage(SQLModel, table=True):
    __tablename__ = "property_image"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    image_url: str = Field(unique=True, min_length=3, max_length=50)
    is_cover: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    property_id: UUID = Field(nullable=False, foreign_key="property.id")
    property: "Property" = Relationship(back_populates="images")

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()
