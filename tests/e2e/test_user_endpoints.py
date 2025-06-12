from src.entities.user import UserRole

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



def test_get_users(client):
    # arrange
    test_user = {
        "username":"tom",
        "email":"test_user@example.com",
        "password":"Password123!",
        "role":UserRole.CLIENT
    }
    test_user_2 = {
        "username":"devo",
        "email":"test_user@example.com",
        "password":"Password123!",
        "role":UserRole.ADMIN
    }

    # act
    client.post("/user", json = test_user)
    client.post("/user", json = test_user_2)
    response = client.get("/user")

    # assert
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    for user in response.json():
        assert isinstance(user, dict)
        assert "username" in user
        assert "email" in user
        assert "role" in user
        # You can also check the values of the fields if you want
        assert user["username"] == test_user["username"]
        assert user["email"] == test_user["email"]
        assert user["role"] == test_user["role"]

