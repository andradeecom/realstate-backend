from sqlmodel import Session, select, delete
from datetime import datetime
from uuid import UUID
import logging
from . import models
from . import repository
from fastapi import Request, Body
from src.database.core import SessionDep
from src.exceptions import UserAlreadyExistsError, InvalidPasswordError, InvalidEmailError, InvalidRoleError, UserPermissionError, UserNotFoundError
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
    db_users = db.exec(select(User)).all()
    users_response = [
        models.GetUsersResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role
        ) for user in db_users
    ]

    return users_response

def get_user_by_id(id: UUID, db: SessionDep):
    db_user = db.exec(select(User).filter(User.id == id)).one_or_none()
    if not db_user:
        logging.error("User not found")
        raise UserNotFoundError()
    return models.GetUserByIdRequest(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        role=db_user.role
    )

def update_user_by_id(id: UUID, db: SessionDep, user: models.UpdateUserByIdRequest = Body(...)):
    # check body of request (PUT) to get fields to update
    db_user = db.exec(select(User).filter(User.id == id)).one_or_none()
    if db_user:
        if user.username:
            db_user.username = user.username
        if user.email:
            db_user.email = user.email
        if user.role:
            db_user.role = user.role
        db_user.updated_at = datetime.now().isoformat()
        db.commit()

    return {"message": "User updated successfully"}

def delete_user_by_id(id: UUID, db: SessionDep):
    result = db.exec(delete(User).where(User.id == id))
    if result == 0:
        logging.error("User not found")
        raise UserNotFoundError()
    db.commit()
    return {"message": f"User was deleted successfully"}
    