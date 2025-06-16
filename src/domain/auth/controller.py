from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.database.core import SessionDep
from . import service, models
from src.entities.user import User
from src.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/signup")
def signup(user_input: models.SignupRequest, db: SessionDep):
    return service.signup(user_input, db)

@router.post("/signin", response_model=models.SigninResponse)
def signin(user_input: models.SigninRequest, db: SessionDep):
    return service.signin(user_input, db)

@router.post("/token")
async def login_for_access_token(db: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token endpoint for Swagger UI authentication
    The username field will be used as email
    """
    return service.signin_with_oauth2_form(form_data, db)

@router.post("/signout")
def signout(
    db: SessionDep,
    current_user: User = Depends(get_current_user)
):
    return service.signout(current_user.id, db)

@router.post("/refresh", response_model=models.RefreshResponse)
def refresh(
    db: SessionDep,
    current_user: User = Depends(get_current_user)
):
    return service.refresh_token(current_user.id, db)
