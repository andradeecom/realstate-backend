"""
Validate the following scenarios:
    - Create user 
    - Get users
    - Get user by id
    - Update user by id
    - Delete user by id
"""

def test_create_user(client, test_user_request):
    response = client.post("/user", json=test_user_request.model_dump())
    assert response.status_code == 201
    assert response.json()["email"] == test_user_request.email
    assert response.json()["role"] == test_user_request.role.value
    assert response.json()["message"] == "User created successfully"
    assert response.json()["status_code"] == 201