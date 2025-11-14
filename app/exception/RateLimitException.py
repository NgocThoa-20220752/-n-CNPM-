from app.exception.BaseAPIException import BaseAPIException


class RateLimitException(BaseAPIException):
    """Exception khi vượt quá rate limit"""

    def __init__(
            self,
            message: str = "Rate limit exceeded",
            retry_after: int = None
    ):
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after}
        )


class TooManyRequestsException(RateLimitException):
    """Exception khi quá nhiều requests"""

    def __init__(self, message: str = "Too many requests", retry_after: int = 60):
        super().__init__(
            message=message,
            retry_after=retry_after
        )


class VerificationAttemptsExceededException(RateLimitException):
    """Exception khi vượt quá số lần xác thực"""

    def __init__(self, message: str = "Maximum verification attempts exceeded", retry_after: int = 300):
        super().__init__(
            message=message,
            retry_after=retry_after
        )