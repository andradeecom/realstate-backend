from fastapi import APIRouter, status, Depends, HTTPException
from uuid import UUID
from src.database.core import SessionDep
from src.domain.users import service, models
from src.auth.dependencies import allow_superadmin_admin, allow_superadmin_admin_employee, allow_update_own_account
from src.entities.user import User

router = APIRouter(
    prefix="/user",
    tags=["User"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(
    user: models.CreateUserRequest, 
    db: SessionDep,
    current_user: User = Depends(allow_superadmin_admin)
):
    """Create a new user (admin only)"""
    return service.create_user(user, db)

@router.get("/")
def get_users(
    db: SessionDep,
    current_user: User = Depends(allow_superadmin_admin_employee)
):
    """Get all users (admin and employees only)"""
    return service.get_users(db)

@router.get("/{id}")
def get_user(
    id: UUID, 
    db: SessionDep,
    current_user: User = Depends(allow_superadmin_admin_employee)
):
    """Get a user by ID (admin and employees only)"""
    return service.get_user_by_id(id, db)

@router.put("/{id}")
def update_user(
    id: UUID, 
    user_update: models.UpdateUserRequest,
    db: SessionDep,
    permission_checker = Depends(allow_update_own_account)
):
    """Update a user
    
    Permissions:
    - Superadmins can update any account
    - Admins can update any account except superadmins
    - Employees can update their own account or client accounts
    - Clients can update only their own account
    """
    # This will raise an exception if the current user doesn't have permission
    current_user = permission_checker(id)
    
    return service.update_user_by_id(id, user_update, db)

@router.delete("/{id}")
def delete_user(
    id: UUID, 
    db: SessionDep,
    current_user: User = Depends(allow_superadmin_admin)
):
    """Delete a user (admin only)"""
    return service.delete_user_by_id(id, db)
