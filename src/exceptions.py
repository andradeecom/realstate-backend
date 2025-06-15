from fastapi import HTTPException, status

class UserError(HTTPException):
    """Base exception for user-related errors"""
    pass

class AuthError(HTTPException):
    """Base exception for authentication errors"""
    pass

class UserAlreadyExistsError(UserError):
    def __init__(self, user_id=None):
        message = "User already exists" if user_id is None else f"User with id {user_id} already exists"
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=message)

class InvalidEmailError(UserError):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format")

class InvalidPasswordError(UserError):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password format")

class InvalidRoleError(UserError):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid role format")

class UserNotFoundError(UserError):
    def __init__(self, user_id=None):
        message = "User not found" if user_id is None else f"User with id {user_id} not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)

class UserCreationError(UserError):
    def __init__(self):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User creation failed")

class CredentialsError(AuthError):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    
class ForbiddenError(AuthError):
    def __init__(self, message: str="Not enough permissions"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=message)
    