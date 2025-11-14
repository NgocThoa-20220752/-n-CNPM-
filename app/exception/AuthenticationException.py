from app.exception.BaseAPIException import BaseAPIException


class AuthenticationException(BaseAPIException):
    """Base exception cho authentication errors"""

    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            **kwargs
        )


class InvalidCredentialsException(AuthenticationException):
    """Exception khi credentials không hợp lệ"""

    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(
            message=message,
            error_code="INVALID_CREDENTIALS"
        )


class TokenExpiredException(AuthenticationException):
    """Exception khi token hết hạn"""

    def __init__(self, message: str = "Token has expired"):
        super().__init__(
            message=message,
            error_code="TOKEN_EXPIRED"
        )


class InvalidTokenException(AuthenticationException):
    """Exception khi token không hợp lệ"""

    def __init__(self, message: str = "Invalid token"):
        super().__init__(
            message=message,
            error_code="INVALID_TOKEN"
        )


class UnauthorizedException(AuthenticationException):
    """Exception khi không có quyền truy cập"""

    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(
            message=message,
            error_code="UNAUTHORIZED"
        )