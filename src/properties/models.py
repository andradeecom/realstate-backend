from uuid import UUID
from pydantic import BaseModel
from typing import Optional

class CreatePropertyRequest(BaseModel):
    title: str
    address: str
    cover_image: Optional[str]

class CreatePropertyResponse(BaseModel):
    id: UUID
    title: str
    address: str
    status_code: int

class GetPropertiesResponse(BaseModel):
    id: UUID
    title: str
    address: str
    cover_image: Optional[str]

class GetPropertyByIdResponse(BaseModel):
    id: UUID
    title: str
    address: str

class UpdatePropertyByIdRequest(BaseModel):
    title: Optional[str] = None
    address: Optional[str] = None
    cover_image: Optional[str] = None