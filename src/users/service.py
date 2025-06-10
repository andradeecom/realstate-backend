from sqlmodel import select
from uuid import UUID
import logging
from . import models
from . import repository
from src.database.core import SessionDep
from src.exceptions import UserAlreadyExistsError, InvalidPasswordError, InvalidEmailError, InvalidRoleError
from src.entities.user import User
from src.lib.utils import validate_email, validate_password, validate_role, hash_password

def create_user(user: models.CreateUserRequest, db: SessionDep) -> models.CreateUserResponse:
    # Validate email
    if not validate_email(user.email):
        logging.error("Invalid email format")
        raise InvalidEmailError()
    # Validate password format
    if not validate_password(user.password):
        logging.error("Invalid password format")
        raise InvalidPasswordError()
    # Validate role format (enum)
    if not validate_role(user.role):
        logging.error("Invalid role format")
        raise InvalidRoleError()
    
    existing_user = db.exec(select(User).filter(User.email == user.email)).one_or_none() # here "query" is deprecated.
    # If user already exists, raise error
    if existing_user:
        logging.error("User already exists")
        raise UserAlreadyExistsError(user_id=existing_user.id)
    
    # Create the new user
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
        role=user.role
    )
    
    logging.info("User created successfully")
    repository.create_user(new_user, db)
    
    return models.CreateUserResponse(
        id=new_user.id,
        email=new_user.email,
        role=new_user.role,
        message="User created successfully",
        status_code=201
    )

def get_users(db: SessionDep):
    # create classes 
    # check role 
    # raise errors
    # return users
    pass

def get_user_by_id(id: UUID, db: SessionDep):
    pass

def update_user_by_id(id: UUID, db: SessionDep):
    # check body of request (PUT) to get fields to update

    pass

def delete_user_by_id(id: UUID, db: SessionDep):
    pass
    