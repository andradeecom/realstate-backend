from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from uuid import UUID
from sqlmodel import select
from pydantic import BaseModel
import jwt

from src.database.core import SessionDep
from src.entities.tenant_user import TenantUser as User, UserRole
from src.exceptions import ForbiddenError, CredentialsError
from src.lib.utils import verify_auth_token

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", scheme_name="Email & Password Auth")

# Token data model
class TokenData(BaseModel):
    user_id: str

# Base dependency to get the current user
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep) -> User:
    """Get the current user from the token"""
    try:
        # Use the verify_auth_token function from utils
        payload = verify_auth_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise CredentialsError()
        token_data = TokenData(user_id=user_id)
    except jwt.PyJWTError:
        raise CredentialsError()
        
    # Get user from database
    user = db.exec(select(User).where(User.id == token_data.user_id)).one_or_none()
    if user is None:
        raise CredentialsError()
        
    return user

# Define permission levels using the current user
class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: Annotated[User, Depends(get_current_user)]):
        if current_user.role not in self.allowed_roles:
            raise ForbiddenError()
        return current_user

# Permission dependencies
allow_superadmin_admin = RoleChecker([UserRole.SUPERADMIN, UserRole.ADMIN])
allow_superadmin_admin_employee = RoleChecker([UserRole.SUPERADMIN, UserRole.ADMIN, UserRole.EMPLOYEE])

# Special dependency for update operations
def allow_update_own_account(current_user: Annotated[User, Depends(get_current_user)], db: SessionDep):
    """
    Allows:
    - Superadmins to update any account
    - Admins to update any account except superadmins
    - Employees to update their own account or client accounts
    - Clients to update only their own account
    """
    # Return a function that checks if the current user can update the target user
    def can_update_user(target_user_id: UUID):
        # If same user, always allow
        if str(target_user_id) == str(current_user.id):
            return current_user
            
        # Check roles
        if current_user.role == UserRole.SUPERADMIN:
            # Superadmins can update any account
            return current_user
        elif current_user.role == UserRole.ADMIN:
            # Admins can update any account except superadmins
            target_user = db.exec(select(User).where(User.id == target_user_id)).one_or_none()
            if target_user and target_user.role == UserRole.SUPERADMIN:
                raise ForbiddenError(message="Not enough permissions to update superadmin accounts")
            return current_user
        elif current_user.role == UserRole.EMPLOYEE:
            # Employees can update client accounts
            target_user = db.exec(select(User).where(User.id == target_user_id)).one_or_none()
            if target_user and target_user.role == UserRole.CLIENT:
                return current_user
            raise ForbiddenError(message="Employees can only update client accounts")
        else:
            # Clients can only update their own account (handled by first check)
            raise ForbiddenError()
    
    return can_update_user
