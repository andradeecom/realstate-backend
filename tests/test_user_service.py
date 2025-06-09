from src.users import service
from unittest.mock import patch
from src.exceptions import InvalidEmailError, InvalidPasswordError, InvalidRoleError, UserAlreadyExistsError

"""Validate the following scenarios:
    - Invalid email format (more unit tests needed)
    - Invalid password format (more unit tests needed)
    - Invalid role format (more unit tests needed)
    - User already exists
    - User created successfully
"""

def test_create_user_invalid_email(db_session, test_user_request):
    # Mock the validate_email function to return False
    with patch('src.users.service.validate_email', return_value=False):
        # The service should raise an InvalidEmailError
        try:
            service.create_user(test_user_request, db_session)
            assert False, "Should have raised InvalidEmailError"
        except InvalidEmailError as e:
            assert e.status_code == 400
            assert e.detail == "Invalid email format"


def test_create_user_invalid_password(db_session, test_user_request):
    # Mock the validate_password function to return False
    with patch('src.users.service.validate_password', return_value=False):
        # The service should raise an InvalidPasswordError
        try:
            service.create_user(test_user_request, db_session)
            assert False, "Should have raised InvalidPasswordError"
        except InvalidPasswordError as e:
            assert e.status_code == 401
            assert e.detail == "Invalid password format"
    
def test_create_user_invalid_role(db_session, test_user_request):
    # Mock the role validation function to return False
    with patch('src.users.service.validate_role', return_value=False):
        try:
            service.create_user(test_user_request, db_session)
            assert False, "Should have raised InvalidRoleError"
        except InvalidRoleError as e:
            assert e.status_code == 401
            assert e.detail == "Invalid role format"
    
def test_create_user_user_already_exists(db_session, test_user_request):
    # First creation should succeed
    test_user_response = service.create_user(test_user_request, db_session)

    # Second creation with the same email should fail
    try:
        service.create_user(test_user_request, db_session)
        assert False, "Should have raised UserAlreadyExistsError"
    except UserAlreadyExistsError as e:
        assert e.status_code == 409
        assert f"User with id {test_user_response.id} already exists" in e.detail

    # Verify the successful response from the first creation
    assert test_user_response.status_code == 201
    assert test_user_response.message == "User created successfully"
    
def test_create_user_user_created_successfully(db_session, test_user_request):
    # The service should return a CreateUserResponse
    test_user_response = service.create_user(test_user_request, db_session)

    assert test_user_response.status_code == 201
    assert test_user_response.message == "User created successfully"
    assert test_user_response.email == test_user_request.email
    assert test_user_response.role == test_user_request.role
    assert test_user_response.id is not None
