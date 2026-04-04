from fastapi import status

class AppException(Exception):
    """Base class for application exceptions."""
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(message)
        
class NotFoundException(AppException):
    def __init__(self, message="Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)

class UnauthorizedException(AppException):
    def __init__(self, message="Unauthorized"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)