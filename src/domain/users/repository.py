from uuid import UUID
from src.entities.user import User
from src.database.core import SessionDep
from sqlmodel import select
from src.domain.users.models import UpdateUserRequest

def get_user_by_id(id: UUID, db: SessionDep) -> User:
    """Get a user by ID"""
    return db.exec(select(User).filter(User.id == id)).one_or_none()

def get_user_by_email(email: str, db: SessionDep) -> User:
    """Get a user by email"""
    return db.exec(select(User).filter(User.email == email)).one_or_none()

def create_user(new_user: User, db: SessionDep) -> User:
    """Create a new user"""
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

def get_all_users(db: SessionDep) -> list[User]:
    """Get all users"""
    return db.exec(select(User)).all()

def update_user(id: UUID, user_update: UpdateUserRequest, db: SessionDep) -> User:
    """Update a user"""
    user = get_user_by_id(id, db)
    
    # Update user attributes if provided in the request
    if user_update.username is not None:
        user.username = user_update.username
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.password is not None:
        user.password_hash = user_update.password  # Already hashed in service
    if user_update.role is not None:
        user.role = user_update.role
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

def delete_user(id: UUID, db: SessionDep) -> None:
    """Delete a user"""
    user = get_user_by_id(id, db)
    
    db.delete(user)
    db.commit()