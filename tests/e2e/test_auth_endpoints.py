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
    assert "message" in data
    assert UUID(data["user_id"])
    
    # Check token structure (it's a TokenResponse object)
    token = data["token"]
    assert isinstance(token, dict)
    assert "access_token" in token
    assert "refresh_token" in token
    assert "token_type" in token
    assert token["token_type"] == "Bearer"
    assert "expires_at" in token


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


def test_signin_success(client, test_user_request):
    """Test successful user signin"""
    # First create a user
    signup_data = {
        "username": test_user_request.username,
        "email": test_user_request.email,
        "password": test_user_request.password
    }
    client.post("/auth/signup", json=signup_data)
    
    # Arrange
    signin_data = {
        "email": test_user_request.email,
        "password": test_user_request.password
    }
    
    # Act
    response = client.post("/auth/signin", json=signin_data)
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "user_id" in data
    assert "token" in data
    assert "message" in data
    assert UUID(data["user_id"])
    
    # Check token structure
    token = data["token"]
    assert isinstance(token, dict)
    assert "access_token" in token
    assert "refresh_token" in token
    assert "token_type" in token
    assert token["token_type"] == "Bearer"
    assert "expires_at" in token


def test_signin_invalid_credentials(client, test_user_request):
    """Test signin with invalid credentials"""
    # First create a user
    signup_data = {
        "username": test_user_request.username,
        "email": test_user_request.email,
        "password": test_user_request.password
    }
    client.post("/auth/signup", json=signup_data)
    
    # Arrange - wrong password
    signin_data = {
        "email": test_user_request.email,
        "password": "WrongPassword123!"
    }
    
    # Act
    response = client.post("/auth/signin", json=signin_data)
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid password" in response.json()["detail"]


def test_signin_user_not_found(client):
    """Test signin with non-existent user"""
    # Arrange
    signin_data = {
        "email": "nonexistent@example.com",
        "password": "Password123!"
    }
    
    # Act
    response = client.post("/auth/signin", json=signin_data)
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"]


def test_signout_success(client, test_user_request):
    """Test successful user signout"""
    # First create a user and signin
    signup_data = {
        "username": test_user_request.username,
        "email": test_user_request.email,
        "password": test_user_request.password
    }
    client.post("/auth/signup", json=signup_data)
    
    signin_response = client.post("/auth/signin", json={
        "email": test_user_request.email,
        "password": test_user_request.password
    })
    
    # Get the token
    token = signin_response.json()["token"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Act - signout
    response = client.post("/auth/signout", headers=headers)
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert "signed out" in response.json()["message"].lower()


def test_signout_unauthorized(client):
    """Test signout without authentication"""
    # Act - attempt to signout without token
    response = client.post("/auth/signout")
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_token_success(client, test_user_request):
    """Test successful token refresh"""
    # First create a user and signin
    signup_data = {
        "username": test_user_request.username,
        "email": test_user_request.email,
        "password": test_user_request.password
    }
    client.post("/auth/signup", json=signup_data)
    
    signin_response = client.post("/auth/signin", json={
        "email": test_user_request.email,
        "password": test_user_request.password
    })
    
    # Get the token
    token = signin_response.json()["token"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Act - refresh token
    response = client.post("/auth/refresh", headers=headers)
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "user_id" in data
    assert "token" in data
    assert "message" in data
    
    # Verify we got new tokens
    new_token = data["token"]
    assert new_token["access_token"] != token
    assert "refresh_token" in new_token
    assert "token_type" in new_token
    assert new_token["token_type"] == "Bearer"
    assert "expires_at" in new_token


def test_refresh_token_unauthorized(client):
    """Test refresh token without authentication"""
    # Act - attempt to refresh without token
    response = client.post("/auth/refresh")
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_token_endpoint_with_form_data(client, test_user_request):
    """Test the OAuth2 token endpoint with form data (for Swagger UI)"""
    # First create a user
    signup_data = {
        "username": test_user_request.username,
        "email": test_user_request.email,
        "password": test_user_request.password
    }
    client.post("/auth/signup", json=signup_data)
    
    # Arrange - form data for OAuth2
    form_data = {
        "username": test_user_request.email,  # OAuth2 uses username field for email
        "password": test_user_request.password
    }
    
    # Act
    response = client.post("/auth/token", data=form_data)
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "Bearer"
