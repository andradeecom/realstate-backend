from src.lib.utils import validate_role

"""
Validate role format
"""

def test_validate_role():
    assert validate_role("admin") == True
    assert validate_role("client") == True
    assert validate_role("superadmin") == True
    assert validate_role("employee") == True
    assert validate_role("CLIENT") == False
    assert validate_role("SELLER") == False
    assert validate_role("BUYER") == False
    assert validate_role("ADMIN") == False
    assert validate_role("buyer") == False
    assert validate_role("seller") == False
