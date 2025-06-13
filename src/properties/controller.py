from fastapi import APIRouter, status, Depends, Body
from uuid import UUID
from src.database.core import SessionDep
from src.properties import service, models

router = APIRouter(
    prefix="/property",
    tags=["Property"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_property(property: models.CreatePropertyRequest, db:SessionDep):
    return service.create_property(property, db)

@router.get("/")
def get_properties(db: SessionDep):
    return service.get_properties(db)

@router.get("/{id}")
def get_property_by_id(id: UUID, db: SessionDep):
    return service.get_property_by_id(id, db)

@router.delete("/{id}")
def delete_property(id: UUID, db: SessionDep):
    return service.delete_property_by_id(id, db)