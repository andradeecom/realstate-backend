from src.users import service
from unittest.mock import patch
from src.exceptions import InvalidEmailError, InvalidPasswordError, InvalidRoleError, UserAlreadyExistsError

"""Validate the following scenarios:
    - Get users
    - Get user by id
"""
