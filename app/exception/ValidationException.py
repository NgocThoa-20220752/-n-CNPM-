from app.exception.BaseAPIException import BaseAPIException


class ValidationException(BaseAPIException):
    """Base exception cho validation errors"""

    def __init__(self, message: str = "Validation failed", **kwargs):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            **kwargs
        )


class InvalidInputException(ValidationException):
    """Exception khi input không hợp lệ"""

    def __init__(self, message: str = "Invalid input", field: str = None, errors: dict = None):
        super().__init__(
            message=message,
            error_code="INVALID_INPUT",
            details={"field": field, "errors": errors or {}}
        )


class WeakPasswordException(ValidationException):
    """Exception khi password yếu"""

    def __init__(self, message: str = "Password is too weak", requirements: list = None):
        super().__init__(
            message=message,
            error_code="WEAK_PASSWORD",
            details={"requirements": requirements or []}
        )


class InvalidEmailException(ValidationException):
    """Exception khi email không hợp lệ"""

    def __init__(self, message: str = "Invalid email format"):
        super().__init__(
            message=message,
            error_code="INVALID_EMAIL"
        )


class InvalidPhoneException(ValidationException):
    """Exception khi số điện thoại không hợp lệ"""

    def __init__(self, message: str = "Invalid phone number"):
        super().__init__(
            message=message,
            error_code="INVALID_PHONE"
        )