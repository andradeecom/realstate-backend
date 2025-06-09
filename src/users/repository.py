from . import models
from src.database.core import SessionDep

def create_user(user: models.CreateUserRequest, db: SessionDep) -> None:
    db.add(user)
    db.commit()