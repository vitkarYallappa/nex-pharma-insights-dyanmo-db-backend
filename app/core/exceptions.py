"""
Simple Custom Exceptions
Basic exceptions for the application
"""

class UserNotFoundException(Exception):
    """Raised when a user is not found"""
    pass

class UserAlreadyExistsException(Exception):
    """Raised when trying to create a user that already exists"""
    pass

class InvalidCredentialsException(Exception):
    """Raised when credentials are invalid"""
    pass 