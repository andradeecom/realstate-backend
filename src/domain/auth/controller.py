from fastapi import APIRouter
from src.database.core import SessionDep
from . import service, models

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/signup")
def signup(user_input: models.SignupRequest, db: SessionDep):
    return service.signup(user_input, db)

@router.post("/signin")
def signin(user_input: models.SigninRequest, db: SessionDep):
    return service.signin(user_input, db)

@router.post("/signout")
def signout(db: SessionDep):
    return service.signout(db)

@router.post("/refresh")
def refresh(db: SessionDep):
    return service.refresh(db)