from . import models
from src.database.core import SessionDep
from sqlmodel import select
from src.entities.user import User

def create_user(user: models.CreateUserRequest, db: SessionDep) -> None:
    db.add(user)
    db.commit()

def get_users(db: SessionDep) -> list[models.GetUsersResponse]:
    return db.exec(select(User)).all()