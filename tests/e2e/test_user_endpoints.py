from fastapi import status
from uuid import UUID

"""
Validate the following scenarios:
    - Create user 
    - Get users
    - Get user by id
    - Update user by id
    - Delete user by id
"""

def test_create_user(client, test_user_request, auth_headers):
    """Test creating a user as an admin"""
    response = client.post(
        "/user", 
        json=test_user_request.model_dump(),
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == test_user_request.email
    assert data["role"] == test_user_request.role.value
    assert "id" in data
    assert UUID(data["id"])

def test_get_users(client, test_user_request, auth_headers):
    """Test getting all users as an admin"""
    # First create a user
    client.post("/user", json=test_user_request.model_dump(), headers=auth_headers)
    
    # Then get all users
    response = client.get("/user", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= 2  # At least the admin user and the created test user

def test_get_user_by_id(client, test_user_request, auth_headers):
    """Test getting a user by ID as an admin"""
    # First create a user
    create_response = client.post("/user", json=test_user_request.model_dump(), headers=auth_headers)
    user_id = create_response.json()["id"]
    
    # Then get the user by ID
    response = client.get(f"/user/{user_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    user = response.json()
    assert user["id"] == user_id
    assert user["email"] == test_user_request.email

def test_update_user(client, test_user_request, auth_headers):
    """Test updating a user as an admin"""
    # First create a user
    create_response = client.post("/user", json=test_user_request.model_dump(), headers=auth_headers)
    user_id = create_response.json()["id"]
    
    # Then update the user
    update_data = {
        "username": "updated_username",
        "email": "updated@example.com",
        "role": "client"
    }
    response = client.put(f"/user/{user_id}", json=update_data, headers=auth_headers)
    updated_user = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert updated_user["email"] == update_data["email"]
    assert updated_user["username"] == update_data["username"]
    assert updated_user["role"] == update_data["role"]
    assert updated_user["is_active"] == True
    assert "message" in updated_user
    assert updated_user["message"] == "User updated successfully"

def test_delete_user(client, test_user_request, auth_headers):
    """Test deleting a user as an admin"""
    # First create a user
    create_response = client.post("/user", json=test_user_request.model_dump(), headers=auth_headers)
    user_id = create_response.json()["id"]
    
    # Then delete the user
    response = client.delete(f"/user/{user_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    # Verify the user is deleted
    get_response = client.get(f"/user/{user_id}", headers=auth_headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND