from src.lib.utils import validate_email

"""
Validate email format
"""

def test_validate_email():
    assert validate_email("test@example.com") == True
    assert validate_email("test@example") == False
    assert validate_email("test@example.") == False
    assert validate_email("@example.com") == False
    assert validate_email("test@.com") == False
