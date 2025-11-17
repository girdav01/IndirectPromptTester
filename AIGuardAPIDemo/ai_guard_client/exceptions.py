"""
Custom exceptions for AI Guard client
"""


class AIGuardException(Exception):
    """Base exception for AI Guard client"""
    pass


class AuthenticationError(AIGuardException):
    """Raised when authentication fails"""
    pass


class ValidationError(AIGuardException):
    """Raised when input validation fails"""
    pass


class RateLimitError(AIGuardException):
    """Raised when rate limit is exceeded"""
    pass


class APIError(AIGuardException):
    """Raised when API returns an error"""
    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response
