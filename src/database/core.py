import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine
from typing import Annotated
from fastapi import Depends
from sqlalchemy.schema import CreateSchema
from sqlalchemy.exc import ProgrammingError

app_env = os.getenv("APP_ENV", "dev")
env_file = f"env/.env.{app_env}"
print(f"Loading environment variables from {env_file}")
load_dotenv(env_file)

# Base engine for database operations
engine = create_engine(os.getenv("DATABASE_URL"))

# Define schemas
GLOBAL_SCHEMA = "real_state_global"

def create_schema(schema_name: str):
    """Create schema if it doesn't exist"""
    with engine.connect() as connection:
        try:
            connection.execute(CreateSchema(schema_name))
            connection.commit()
            print(f"Schema '{schema_name}' created successfully")
        except ProgrammingError:
            connection.rollback()
            print(f"Schema '{schema_name}' already exists")

def init_db():
    """Initialize the database with schemas and tables"""
    # Create schemas
    create_schema(GLOBAL_SCHEMA)
    
    # Create tables in global schema
    from src.entities.user import User, Token, Property
    
    # Set schema for User and Token models
    User.__table__.schema = GLOBAL_SCHEMA
    Token.__table__.schema = GLOBAL_SCHEMA
    Property.__table__.schema = GLOBAL_SCHEMA
    
    # Create all tables at once
    SQLModel.metadata.create_all(engine)
    
    print("All tables created successfully")


def get_session():
    """Get a database session"""
    with Session(engine) as session:
        yield session

def drop_db():
    """Drop all tables in all schemas"""
    print("Dropping all database tables...")
    SQLModel.metadata.drop_all(engine)
    print("All tables dropped successfully")
    
SessionDep = Annotated[Session, Depends(get_session)]