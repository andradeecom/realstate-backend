import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database.core import create_schema
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.schema import DropSchema
from sqlalchemy.ext.compiler import compiles
from src.users.models import CreateUserRequest
from src.properties.models import CreatePropertyRequest
from src.entities.user import UserRole

import os
from dotenv import load_dotenv
import uuid

app_env = os.getenv("APP_ENV", "test")
env_file = f"env/.env.{app_env}"
print(f"Loading environment variables from {env_file}")
load_dotenv(env_file)

TEST_SCHEMA = "test_schema"

# Add CASCADE option to DropSchema
@compiles(DropSchema, "postgresql")
def _compile_drop_schema(element, compiler, **kw):
    return compiler.visit_drop_schema(element) + " CASCADE"

@pytest.fixture
def db_session():
    # Use a unique schema for each test run to ensure isolation
    test_schema_name = f"{TEST_SCHEMA}_{uuid.uuid4().hex[:8]}"

    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set")

    testing_engine = create_engine(DATABASE_URL)
    
    create_schema(test_schema_name)

    # Import models here to avoid circular imports
    from src.entities.user import User, Token

    # Set schema for User and Token models
    User.__table__.schema = test_schema_name
    Token.__table__.schema = test_schema_name
    
    SQLModel.metadata.create_all(testing_engine)

    with Session(testing_engine) as session:
        try:
            yield session
        finally:
            session.close()

    # Clean up after tests - drop the entire schema with CASCADE
    with testing_engine.begin() as conn:
        conn.execute(DropSchema(test_schema_name))
        
    testing_engine.dispose()
    
@pytest.fixture
def test_user_request():
    return CreateUserRequest(
        username="test_user",
        email="test_user@example.com",
        password="Password123!",
        role=UserRole.CLIENT
    )

@pytest.fixture
def test_property_request():
    return CreatePropertyRequest(
        title="test+property",
        address="test_address",
        cover_image="test_image.path"
    )


@pytest.fixture
def client(db_session):
    # Use dependency override to use the test session
    def get_test_session():
        yield db_session
    
    app.dependency_overrides = {}  # Clear any previous overrides

    # Override the session dependency
    from src.database.core import get_session
    app.dependency_overrides[get_session] = get_test_session
    
    test_client = TestClient(app)
    yield test_client
    # Clean up
    app.dependency_overrides = {}