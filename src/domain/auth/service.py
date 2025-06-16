from uuid import UUID
from src.database.core import SessionDep
from src.domain.users import service as users_service
from src.domain.users.models import CreateUserRequest
from src.lib.utils import generate_auth_token, verify_password
from src.exceptions import CredentialsError
from . import repository
from datetime import timedelta
from . import models, repository
from src.exceptions import UserNotFoundError, InvalidPasswordError
import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

def signup(user_input: models.SignupRequest, db: SessionDep) -> models.SignupResponse:
    # Convert SignupRequest to CreateUserRequest
    create_request = CreateUserRequest(
        username=user_input.username,
        email=user_input.email,
        password=user_input.password,
        role=user_input.role  # Use the role from the request (defaults to CLIENT)
    )
    
    # Reuse the user creation logic
    user = users_service.create_user(create_request, db)
    
    # Generate auth tokens
    access_token = generate_auth_token(user.id, "auth", timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = generate_auth_token(user.id, "refresh", timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

    token = repository.create_tokens(user.id, access_token, refresh_token, db)
    
    # Return auth response
    return models.SignupResponse(
        user_id=user.id,
        token=token,
        message="User signed up successfully"
    )

def signin(user_input: models.SigninRequest, db: SessionDep) -> models.SigninResponse:
    user = users_service.get_user_by_email(user_input.email, db)
    if not user:
        raise UserNotFoundError(user_id=user_input.email)

    if not verify_password(user_input.password, user.password_hash):
        raise InvalidPasswordError()
    
    access_token = generate_auth_token(user.id, "auth", timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = generate_auth_token(user.id, "refresh", timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    
    # check if user already has a token
    existing_token = repository.get_token_by_user_id(user.id, db)
    if existing_token:
        repository.delete_token(user.id, db)

    token = repository.create_tokens(user.id, access_token, refresh_token, db)
    
    return models.SigninResponse(
        user_id=user.id,
        token=token,
        message="User signed in successfully"
    )

def signin_with_oauth2_form(form_data, db: SessionDep):
    """
    Handle OAuth2 form authentication for Swagger UI
    The username field is used as email
    
    Returns a format compatible with OAuth2 in Swagger UI
    """
    try:
        # Create a SigninRequest using the username field as email
        signin_request = models.SigninRequest(
            email=form_data.username,  # Use username field as email
            password=form_data.password
        )
        # Get the regular signin response
        signin_response = signin(signin_request, db)
        
        # For OAuth2 in Swagger UI, we need to return the token in the expected format
        from fastapi import HTTPException, status
        from fastapi.responses import JSONResponse
        
        # Return the token in the format expected by Swagger UI
        return {
            "access_token": signin_response.token.access_token,
            "token_type": "Bearer",
            "expires_at": signin_response.token.expires_at.isoformat(),
            "refresh_token": signin_response.token.refresh_token,
            "user_id": str(signin_response.user_id),
            "message": signin_response.message
        }
    except UserNotFoundError:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidPasswordError:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

def signout(user_id: UUID, db: SessionDep) -> models.SignoutResponse:
    """Sign out the current user"""
    # Delete the user's token
    repository.delete_token(user_id, db)
    return models.SignoutResponse(message="User signed out successfully")
    
def refresh_token(user_id: UUID, db: SessionDep) -> models.RefreshResponse:
    """Refresh the current user's access token using the authenticated user from the token
    
    Args:
        user_id (UUID): User ID from the current authenticated user
        db (SessionDep): Database session
        
    Returns:
        models.RefreshResponse: New access and refresh tokens
        
    Raises:
        CredentialsError: If user has no valid token
    """
    # Get the user's current token from database
    token = repository.get_token_by_user_id(user_id, db)
    if not token:
        raise CredentialsError(message="No valid token found")
        
    # Generate new tokens
    access_token = generate_auth_token(
        user_id=user_id,
        token_type="access",
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    refresh_token = generate_auth_token(
        user_id=user_id,
        token_type="refresh",
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    # Delete old token and create new ones
    repository.delete_token(user_id, db)
    token_response = repository.create_tokens(user_id, access_token, refresh_token, db)
    
    return models.RefreshResponse(
        user_id=user_id,
        token=token_response,
        message="Token refreshed successfully"
    )


