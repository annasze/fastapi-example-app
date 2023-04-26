from fastapi import HTTPException, status


class InvalidCredentialsException(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_403_FORBIDDEN
        self.detail = "Invalid credentials."


class NotAuthorizedException(HTTPException):
    def __init__(self):
        self.status_code=status.HTTP_403_FORBIDDEN
        self.detail = "Not authorized to perform requested action."


