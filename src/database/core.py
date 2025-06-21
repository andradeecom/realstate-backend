import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine
from typing import Annotated, Optional
from fastapi import Depends, Header
from sqlalchemy.schema import CreateSchema
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker
from contextvars import ContextVar
from sqlalchemy import select

app_env = os.getenv("APP_ENV", "dev")
env_file = f"env/.env.{app_env}"
print(f"Loading environment variables from {env_file}")
load_dotenv(env_file)

# Base engine for database operations
engine = create_engine(os.getenv("DATABASE_URL"))

# Define schemas
GLOBAL_SCHEMA = "public"

# Context variable to store the current tenant ID
current_tenant_id: ContextVar[Optional[str]] = ContextVar('current_tenant_id', default=None)

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

def get_tenant_schema(tenant_id: str) -> str:
    """Get schema name for a tenant"""
    if not tenant_id:
        return GLOBAL_SCHEMA
    return f"tenant_{tenant_id}"

def get_current_tenant_id() -> Optional[str]:
    """Get the current tenant ID from context"""
    return current_tenant_id.get()

def set_tenant_for_request(tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID")) -> Optional[str]:
    """Set the tenant ID for the current request"""
    if tenant_id:
        current_tenant_id.set(tenant_id)
        # Ensure the tenant schema exists
        tenant_schema = get_tenant_schema(tenant_id)
        create_schema(tenant_schema)
    return tenant_id

def init_db():
    """Initialize the database with schemas and tables"""
    # Create global schema
    create_schema(GLOBAL_SCHEMA)
    
    # Import entity models
    from src.entities import public_user, public_token, public_plan, public_tenant, public_stripe_account, public_domain_verification
    from src.entities import tenant_user, tenant_client, tenant_property, tenant_property_image, tenant_reservation
    
    # Public schema tables
    public_user.PublicUser.__table__.schema = GLOBAL_SCHEMA
    public_token.Token.__table__.schema = GLOBAL_SCHEMA
    public_plan.Plan.__table__.schema = GLOBAL_SCHEMA
    public_tenant.Tenant.__table__.schema = GLOBAL_SCHEMA
    public_stripe_account.StripeAccount.__table__.schema = GLOBAL_SCHEMA
    public_domain_verification.DomainVerification.__table__.schema = GLOBAL_SCHEMA 

    # Create all global tables
    SQLModel.metadata.create_all(engine, tables=[table for table in SQLModel.metadata.tables.values() 
                                                if table.schema == GLOBAL_SCHEMA])
    print("Global tables created successfully")
    
    # Get all tenants from the database and create their schemas
    with Session(engine) as session:
        try:
            from src.entities.public_tenant import Tenant
            tenants = session.exec(select(Tenant)).all()
            for tenant in tenants:
                tenant_schema = get_tenant_schema(tenant.id)
                create_schema(tenant_schema)
                
                # Set tenant schema for tenant-specific tables
                tenant_user.TenantUser.__table__.schema = tenant_schema
                tenant_client.Client.__table__.schema = tenant_schema
                tenant_property.Property.__table__.schema = tenant_schema
                tenant_property_image.PropertyImage.__table__.schema = tenant_schema
                tenant_reservation.Reservation.__table__.schema = tenant_schema
                
                # Create tenant tables
                SQLModel.metadata.create_all(engine, tables=[table for table in SQLModel.metadata.tables.values() 
                                                           if table.schema == tenant_schema])
                print(f"Tables for tenant {tenant.id} created successfully")
        except Exception as e:
            print(f"Error initializing tenant schemas: {e}")

# We do not use for now, but it's important to have it
def create_tenant(tenant_id: str):
    """
    Create a new tenant schema.

    Provides a clean API for programmatically creating tenants (e.g., during tenant onboarding).
    It could be used in admin interfaces or management commands
    """
    tenant_schema = get_tenant_schema(tenant_id)
    create_schema(tenant_schema)
    
    # Import tenant models
    from src.entities import tenant_user, tenant_client, tenant_property, tenant_property_image, tenant_reservation
    
    # Set schema for tenant models
    tenant_user.User.__table__.schema = tenant_schema
    tenant_client.Client.__table__.schema = tenant_schema
    tenant_property.Property.__table__.schema = tenant_schema
    tenant_property_image.PropertyImage.__table__.schema = tenant_schema
    tenant_reservation.Reservation.__table__.schema = tenant_schema
    
    # Create tenant tables
    SQLModel.metadata.create_all(engine, tables=[table for table in SQLModel.metadata.tables.values() 
                                               if table.schema == tenant_schema])
    print(f"Tables for tenant {tenant_id} created successfully")

def get_session(tenant_id: str = Depends(set_tenant_for_request)):
    """Get a database session for the current tenant"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # If we have a tenant ID, set the search path to include the tenant schema
        if tenant_id:
            tenant_schema = get_tenant_schema(tenant_id)
            # Run SQL query to set the search path...
            session.execute(f"SET search_path TO {tenant_schema}, {GLOBAL_SCHEMA}")
        else:
            session.execute(f"SET search_path TO {GLOBAL_SCHEMA}")
            
        yield session
    finally:
        session.close()

def drop_db():
    """Drop all tables in all schemas"""
    print("Dropping all database tables...")
    
    # Drop global tables first
    SQLModel.metadata.drop_all(engine, tables=[table for table in SQLModel.metadata.tables.values() 
                                             if table.schema == GLOBAL_SCHEMA])
    
    # Get all tenant schemas and drop their tables
    with engine.connect() as connection:
        # Query to get all schemas that start with 'tenant_'
        schemas = connection.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'tenant_%'")
        for schema in schemas:
            schema_name = schema[0]
            print(f"Dropping tables in schema {schema_name}...")
            connection.execute(f"DROP SCHEMA {schema_name} CASCADE")
    
    print("All tables dropped successfully")
    
SessionDep = Annotated[Session, Depends(get_session)]