from fastapi import APIRouter, status
from uuid import UUID
from src.database.core import SessionDep
from src.domain.users import service, models

router = APIRouter(
    prefix="/user",
    tags=["User"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user: models.CreateUserRequest, db: SessionDep):
    return service.create_user(user, db)

@router.get("/")
def get_users(db: SessionDep):
    pass

@router.get("/{id}")
def get_user(id: UUID, db: SessionDep):
    pass

@router.put("/{id}")
def update_user(id: UUID, db: SessionDep):
    pass

@router.delete("/{id}")
def delete_user(id: UUID, db: SessionDep):
    pass
