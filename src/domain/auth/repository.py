from src.entities.user import Token, TokenResponse
from src.database.core import SessionDep
from uuid import UUID
from datetime import datetime, timedelta
from sqlmodel import select
from . import service

def create_tokens(user_id: UUID, access_token: str, refresh_token: str, db: SessionDep) -> TokenResponse:
    token = Token(
        user_id=user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=datetime.now() + timedelta(minutes=service.ACCESS_TOKEN_EXPIRE_MINUTES),
        created_at=datetime.now()
    )

    db.add(token)
    db.commit()
    db.refresh(token)

    token_response = TokenResponse(
        access_token=token.access_token,
        refresh_token=token.refresh_token,
        token_type="Bearer",
        expires_at=token.expires_at
    )
    
    return token_response

def get_token_by_user_id(user_id: UUID, db: SessionDep) -> Token | None:
    token = db.exec(select(Token).filter(Token.user_id == user_id)).one_or_none()
    if not token:
        return None
    
    return token

def delete_token(user_id: UUID, db: SessionDep) -> None:
    token = get_token_by_user_id(user_id, db)
    if not token:
        return
    
    db.delete(token)
    db.commit()
