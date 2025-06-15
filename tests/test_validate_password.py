from src.lib.utils import validate_password

"""
Validate password meets security requirements:
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character
"""

def test_validate_password():
    assert validate_password("Password123!") == True
    assert validate_password("password123!") == False
    assert validate_password("Password123") == False
    assert validate_password("Password") == False
    assert validate_password("12345678") == False   
    assert validate_password("PASSWORD123!") == False
    assert validate_password("password") == False
    assert validate_password("pass") == False
    