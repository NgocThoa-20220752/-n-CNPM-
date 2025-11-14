from app.exception.BaseAPIException import BaseAPIException


class VerificationException(BaseAPIException):
    """Base exception cho verification errors"""

    def __init__(self, message: str = "Verification failed", **kwargs):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VERIFICATION_ERROR",
            **kwargs
        )


class InvalidVerificationCodeException(VerificationException):
    """Exception khi mã xác thực không đúng"""

    def __init__(self, message: str = "Invalid verification code", attempts_left: int = None):
        super().__init__(
            message=message,
            error_code="INVALID_VERIFICATION_CODE",
            details={"attempts_left": attempts_left}
        )


class VerificationCodeExpiredException(VerificationException):
    """Exception khi mã xác thực hết hạn"""

    def __init__(self, message: str = "Verification code has expired"):
        super().__init__(
            message=message,
            error_code="VERIFICATION_CODE_EXPIRED"
        )


class VerificationNotFoundException(VerificationException):
    """Exception khi không tìm thấy verification"""

    def __init__(self, message: str = "No verification found"):
        super().__init__(
            message=message,
            error_code="VERIFICATION_NOT_FOUND"
        )