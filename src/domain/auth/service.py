from src.database.core import SessionDep
from src.domain.users import service as users_service
from src.domain.users.models import CreateUserRequest
from src.lib.utils import generate_auth_token
from datetime import timedelta
from . import models

def signup(user_input: models.SignupRequest, db: SessionDep) -> models.SignupResponse:
    # Review this logic. We need save the token in the database (table Token) and relate it to the user
    # Convert SignupRequest to CreateUserRequest
    create_request = CreateUserRequest(
        username=user_input.username,
        email=user_input.email,
        password=user_input.password,
        role=user_input.role  # Use the role from the request (defaults to CLIENT)
    )
    
    # Reuse the user creation logic
    user = users_service.create_user(create_request, db)
    
    # Generate auth token
    token = generate_auth_token(user.id, "auth", timedelta(minutes=15))
    
    # Return auth response
    return models.SignupResponse(
        user_id=user.id,
        token=token
    )

def signin(user_input: models.SigninRequest, db: SessionDep) -> models.SigninResponse:
    # Review this logic. We need save the token in the database (table Token) and relate it to the user
    user = users_service.get_user_by_email(user_input.email, db)
    if not user:
        raise UserNotFoundError(user_id=user_input.email)
    
    if not verify_password(user_input.password, user.password_hash):
        raise InvalidPasswordError()
    
    access_token = generate_auth_token(user.id, "auth", timedelta(minutes=15))
    refresh_token = generate_auth_token(user.id, "refresh", timedelta(days=7))
    
    return models.SigninResponse(
        user_id=user.id,
        access_token=access_token,
        refresh_token=refresh_token,
        message="User signed in successfully"
    )

def signout(db: SessionDep) -> models.SignoutResponse:
    pass
    
def refresh(db: SessionDep) -> models.RefreshResponse:
    pass
