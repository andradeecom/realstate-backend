from src.entities.user import User
from src.database.core import SessionDep
from sqlmodel import select

def existing_user(email: str, db: SessionDep) -> User:
    return db.exec(select(User).filter(User.email == email)).one_or_none()

def create_user(new_user: User, db: SessionDep) -> User:
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user