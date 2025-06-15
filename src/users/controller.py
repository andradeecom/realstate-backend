from fastapi import APIRouter, status, Depends, Body
from uuid import UUID
from src.database.core import SessionDep
from src.users import service, models

router = APIRouter(
    prefix="/user",
    tags=["User"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user: models.CreateUserRequest, db: SessionDep):
    return service.create_user(user, db)

@router.get("/")
def get_users(db: SessionDep):
    # check authorization
    return service.get_users(db)

@router.get("/{id}")
def get_user(id: UUID, db: SessionDep):
    return service.get_user_by_id(id, db)

@router.put("/{id}")
def update_user(id: UUID, db: SessionDep, user: models.UpdateUserByIdRequest):
    return service.update_user_by_id(id, db, user)

@router.delete("/{id}")
def delete_user(id: UUID, db: SessionDep):
    return service.delete_user_by_id(id, db)
