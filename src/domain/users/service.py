from uuid import UUID, uuid4
import logging
from . import models
from . import repository
from src.database.core import SessionDep
from src.exceptions import UserAlreadyExistsError, InvalidPasswordError, InvalidEmailError, InvalidRoleError, UserCreationError
from src.entities.user import User
from src.lib.utils import validate_email, validate_password, validate_role, hash_password

def create_user(user_input: models.CreateUserRequest, db: SessionDep) -> models.CreateUserResponse:
    # Validate email
    if not validate_email(user_input.email):
        logging.error("Invalid email format")
        raise InvalidEmailError()
    # Validate password format
    if not validate_password(user_input.password):
        logging.error("Invalid password format")
        raise InvalidPasswordError()
    # Validate role format (enum)
    if not validate_role(user_input.role):
        logging.error("Invalid role format")
        raise InvalidRoleError()
    
    existing_user = repository.get_user_by_email(user_input.email, db)

    if existing_user:
        logging.error("User already exists")
        raise UserAlreadyExistsError(user_id=existing_user.id)
    
    # Create the new user
    new_user = User(
        id=uuid4(),
        username=user_input.username,
        email=user_input.email,
        password_hash=hash_password(user_input.password),
        role=user_input.role
    )

    db_user = repository.create_user(new_user, db)
    if not db_user:
        logging.error("User creation failed")
        raise UserCreationError()
    
    logging.info("User created successfully")
    
    return models.CreateUserResponse(
        id=db_user.id,
        email=db_user.email,
        role=db_user.role,
        message="User created successfully",
        status_code=201
    )

def get_users(db: SessionDep):
    """Get all users"""
    return repository.get_all_users(db)

def get_user_by_id(id: UUID, db: SessionDep):
    """Get a user by ID"""
    from src.exceptions import UserNotFoundError
    
    user = repository.get_user_by_id(id, db)
    if not user:
        raise UserNotFoundError(user_id=id)
    return user

def update_user_by_id(id: UUID, user_update: models.UpdateUserRequest, db: SessionDep) -> models.UpdateUserResponse:
    """Update a user by ID"""
    from src.exceptions import UserNotFoundError, InvalidEmailError, InvalidPasswordError, InvalidRoleError
    
    # Get the existing user
    user = repository.get_user_by_id(id, db)
    if not user:
        raise UserNotFoundError(user_id=id)
    
    # Validate email if provided
    if user_update.email is not None:
        if not validate_email(user_update.email):
            raise InvalidEmailError()
        # Check if email already exists for another user
        existing_user = repository.get_user_by_email(user_update.email, db)
        if existing_user and existing_user.id != id:
            raise UserAlreadyExistsError(user_id=existing_user.id)
    
    # Validate password if provided
    if user_update.password is not None:
        if not validate_password(user_update.password):
            raise InvalidPasswordError()
        # Hash the new password
        user_update.password = hash_password(user_update.password)
    
    # Validate role if provided
    if user_update.role is not None:
        if not validate_role(user_update.role):
            raise InvalidRoleError()
    
    # Update the user
    updated_user = repository.update_user(id, user_update, db)
    
    return models.UpdateUserResponse(
        id=updated_user.id,
        username=updated_user.username,
        email=updated_user.email,
        role=updated_user.role,
        is_active=updated_user.is_active,
        message="User updated successfully"
    )

def delete_user_by_id(id: UUID, db: SessionDep):
    """Delete a user by ID"""
    from src.exceptions import UserNotFoundError
    
    user = repository.get_user_by_id(id, db)
    if not user:
        raise UserNotFoundError(user_id=id)
    
    repository.delete_user(id, db)
    
    return {"message": f"User with id {id} deleted successfully"}
    