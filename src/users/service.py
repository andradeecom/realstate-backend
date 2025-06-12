from sqlmodel import Session, select, delete
from uuid import UUID
import logging
from . import models
from . import repository
from fastapi import Request, Body
from src.database.core import SessionDep
from src.exceptions import UserAlreadyExistsError, InvalidPasswordError, InvalidEmailError, InvalidRoleError, UserPermissionError
from src.entities.user import User
from src.lib.utils import validate_email, validate_password, validate_role, hash_password, get_current_user_id

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

def get_users(db: SessionDep) -> list[models.GetUsersResponse]:
    # create classes 
    # check role 
    current_user_id = get_current_user_id(request = Request)
    current_user = db.exec(select(User).filter(User.id == current_user_id)).one_or_none()
    # raise errors
    if  current_user.role == models.UserRole.CLIENT:
        raise UserPermissionError("You are not authorized to get users")
    # return users
    return db.exec(select(User)).all()

def get_user_by_id(id: UUID, db: SessionDep):
    return db.exec(select(User).filter(User.id == id)).one_or_none()

def update_user_by_id(id: UUID, db: SessionDep, user: models.UpdateUserByIdRequest = Body(...)):
    # check body of request (PUT) to get fields to update
    db_user = db.exec(select(User).filter(User.id == id)).one_or_none()
    if db_user:
        if user.username:
            db_user.username = user.username
        if user.email:
            db_user.email = user.email
        if user.password_hash:
            # assume this field was already password checked and that this request only contains the new password
            # Hash new password
            db_user.password_hash = hash_password(user.password_hash)
        if user.role:
            db_user.role = user.role
        db.commit()

    return db_user.model_dump(exclude={"password_hash"})

def delete_user_by_id(id: UUID, db: SessionDep):
    db.exec(delete(User).where(User.id == id))
    db.commit()
    return {f"message": "User with id '{id}' deleted successfully"}
    