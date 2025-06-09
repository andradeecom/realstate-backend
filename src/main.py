from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from src.database import database
from typing import Annotated    

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)
    secret_name: str

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

async def startup_event():
    await database.connect()


@app.post("/heroes/")
def create_hero(hero: Hero, session: SessionDep) -> Hero:
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@app.get("/heroes/")
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Hero]:
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes


@app.get("/heroes/{hero_id}")
def read_hero(hero_id: int, session: SessionDep) -> Hero:
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}

@app.get("/")
def read_root():
    return {"msg": "Welcome to the real estate API"}

@app.get("/register")
def read_register():
    return {"msg": "Welcome to the register page"}

@app.get("/login")
def read_login():
    return {"msg": "Welcome to the login page"}

@app.get("/logout")
def read_logout():
    return {"msg": "Welcome to the logout page"}

@app.get("/users")
def read_users():
    return {"msg": "Welcome to the users page"}

@app.get("users/{user_id}")
def read_user(user_id: int):
    return {"msg": f"Welcome to the user page for user Nb: {user_id}"}

@app.post("users/{user_id}")
def create_user(user_id: int):
    return {"msg": f"Welcome to the user page for user Nb: {user_id}"}

@app.put("users/{user_id}")
def update_user(user_id: int):
    return {"msg": f"Welcome to the user page for user Nb: {user_id}"}