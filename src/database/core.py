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
GLOBAL_SCHEMA = "public"
# Need to create new schema for every new tenant
TENANT_SCHEMA = "tenant"

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
    create_schema(TENANT_SCHEMA)
    
    # Create tables in global schema
    from src.entities import public_user, public_plan, public_tenant, public_stripe_account, public_domain_verification, tenant_user
    
    # Public schema tables
    public_user.User.__table__.schema = GLOBAL_SCHEMA
    public_user.Token.__table__.schema = GLOBAL_SCHEMA
    public_plan.Plan.__table__.schema = GLOBAL_SCHEMA
    public_tenant.Tenant.__table__.schema = GLOBAL_SCHEMA
    public_stripe_account.StripeAccount.__table__.schema = GLOBAL_SCHEMA
    public_domain_verification.DomainVerification.__table__.schema = GLOBAL_SCHEMA 

    # Tenant schema tables
    tenant_user.User.__table__.schema = TENANT_SCHEMA
    
    # Create all tables
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