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
    
    existing_user = repository.existing_user(user_input.email, db)

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
    pass

def get_user_by_id(id: UUID, db: SessionDep):
    pass

def update_user_by_id(id: UUID, db: SessionDep):
    pass

def delete_user_by_id(id: UUID, db: SessionDep):
    pass
    