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

def test_get__user_by_id(client, test_user_request):
    # arrange
    created_user = client.post("/user", json=test_user_request.model_dump())
    created_user_id = created_user.json()["id"] 
    # act
    response = client.get(f"/user/{created_user_id}")
    # assert
    assert isinstance(response.json(), dict)
    assert response.json()["email"] == test_user_request.email
    assert response.json()["username"] == test_user_request.username
    assert response.json()["role"] == test_user_request.role.value
    assert response.json()["id"] == created_user_id

def test_update_user_by_id(client, test_user_request):
    # arrange
    created_user = client.post("/user", json=test_user_request.model_dump())
    created_user_id = created_user.json()["id"]
    modifications = [
        {
            "email": "modified@user.com",
            "username": "modified",
            "role": "admin"
        },
        {
            "email": "modified@user.com",
            "username": "modified"
        },
        {
            "email": "modified@user.com",
            "role": "admin"
        },
        {
            "username": "modified",
            "role": "admin"
        },
        {
            "email": "modified@user.com"
        },
        {
            "username": "modified"
        },
        {
            "role": "admin"
        }
    ]
    for mod in modifications:
        # act
        put_response = client.put(f"/user/{created_user_id}", json=mod)

        # Check for correct status code and response
        assert put_response.status_code == 200, f"Update failed with status {put_response.status_code} and detail: {put_response.json()}"

        response = client.get(f"/user/{created_user_id}")
        # assert
        if "username" in mod:
            assert response.json()["username"] == mod["username"]
        if "email" in mod:
            assert response.json()["email"] == mod["email"]
        if "role" in mod:
            assert response.json()["role"] == mod["role"]

def test_delete_user_by_id(client, test_user_request):
    # arrange
    created_user = client.post("/user", json=test_user_request.model_dump())
    created_user_id = created_user.json()["id"]
    # act
    client.delete(f"/user/{created_user_id}")
    response = client.get(f"/user/{created_user_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
