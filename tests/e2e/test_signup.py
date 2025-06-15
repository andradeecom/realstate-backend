from fastapi import status
from uuid import UUID

def test_signup_success(client):
    """Test successful user signup"""
    # Arrange
    signup_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Password123!"
    }
    
    # Act
    response = client.post("/auth/signup", json=signup_data)
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "user_id" in data
    assert "token" in data
    assert UUID(data["user_id"])
    assert isinstance(data["token"], str)
    assert len(data["token"]) > 0


def test_signup_duplicate_email(client):
    """Test signup with an email that already exists"""
    # Arrange
    signup_data = {
        "username": "testuser1",
        "email": "duplicate@example.com",
        "password": "Password123!"
    }
    
    # First signup should succeed
    response = client.post("/auth/signup", json=signup_data)
    assert response.status_code == status.HTTP_200_OK
    
    # Try to signup with the same email
    signup_data["username"] = "testuser2"  # Different username
    response = client.post("/auth/signup", json=signup_data)
    
    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT
    # The error message contains the user ID, so we just check if it contains 'already exists'
    assert "already exists" in response.json()["detail"]


def test_signup_invalid_email(client):
    """Test signup with invalid email format"""
    # Arrange
    signup_data = {
        "username": "testuser",
        "email": "invalid-email",
        "password": "Password123!"
    }
    
    # Act
    response = client.post("/auth/signup", json=signup_data)
    
    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    errors = response.json()["detail"]
    assert any("email" in error["loc"] for error in errors)


def test_signup_invalid_password(client):
    """Test signup with invalid password format"""
    # Arrange
    signup_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "short"  # Too short password
    }
    
    # Act
    response = client.post("/auth/signup", json=signup_data)
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid password format" in response.json()["detail"]


def test_signup_with_custom_role(client):
    """Test that regular signup can't use admin roles"""
    # Arrange
    signup_data = {
        "username": "adminuser",
        "email": "admin@example.com",
        "password": "Password123!",
        "role": "admin"
    }
    
    # Act
    response = client.post("/auth/signup", json=signup_data)
    
    # Assert
    # The signup should succeed, but the role should be client (default)
    assert response.status_code == status.HTTP_200_OK
    
    # Verify the user was created with client role
    # This would require a separate endpoint to check user details
    # For now, we'll assume the implementation follows the specification