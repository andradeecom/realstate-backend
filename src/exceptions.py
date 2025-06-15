from fastapi import HTTPException

class UserError(HTTPException):
    """Base exception for user-related errors"""
    pass

class UserAlreadyExistsError(UserError):
    def __init__(self, user_id=None):
        message = "User already exists"
        super().__init__(status_code=409, detail=message)

class UserPermissionError(UserError):
    def __init__(self):
        message = "User does not have permission" 
        super().__init__(status_code=403, detail=message)

class InvalidEmailError(UserError):
    def __init__(self):
        super().__init__(status_code=400, detail="Invalid email format")

class InvalidPasswordError(UserError):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid password format")

class InvalidRoleError(UserError):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid role format")

class UserNotFoundError(UserError):
    def __init__(self, user_id=None):
        message = "User not found" if user_id is None else f"User with id {user_id} not found"
        super().__init__(status_code=404, detail=message)

