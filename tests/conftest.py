import os
import uuid
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database.core import create_schema
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.schema import DropSchema
from sqlalchemy.ext.compiler import compiles
from src.domain.users.models import CreateUserRequest
from src.entities.tenant_user import TenantUser as UserRole
from src.lib.utils import generate_auth_token
from datetime import timedelta

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
    from src.entities.tenant_user import TenantUser as User, Token

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
def admin_user(db_session):
    """Create an admin user for testing"""
    from src.lib.utils import crypt_context
    from src.entities.tenant_user import TenantUser as User
    
    # Create admin user with properly hashed password
    admin = User(
        username="admin_user",
        email="admin@example.com",
        password_hash=crypt_context.hash("Admin123!"),  # Properly hash the password
        role=UserRole.ADMIN
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin

@pytest.fixture
def admin_token(admin_user):
    """Generate a token for the admin user"""
    return generate_auth_token(admin_user.id, "auth", timedelta(minutes=30))

@pytest.fixture
def auth_headers(admin_token):
    """Create authorization headers with admin token"""
    return {"Authorization": f"Bearer {admin_token}"}

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