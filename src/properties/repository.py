from . import models
from src.database.core import SessionDep
from sqlmodel import select
from src.entities.user import Property

def create_property(property: models.CreatePropertyRequest, db: SessionDep) -> None:
    db.add(property)
    db.commit()