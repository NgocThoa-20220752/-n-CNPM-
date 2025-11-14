from app.exception.BaseAPIException import BaseAPIException


class BusinessLogicException(BaseAPIException):
    """Base exception cho business logic errors"""

    def __init__(self, message: str = "Business logic error", **kwargs):
        super().__init__(
            message=message,
            status_code=400,
            error_code="BUSINESS_LOGIC_ERROR",
            **kwargs
        )


class AccountNotActiveException(BusinessLogicException):
    """Exception khi tài khoản chưa active"""

    def __init__(self, message: str = "Account is not active"):
        super().__init__(
            message=message,
            error_code="ACCOUNT_NOT_ACTIVE"
        )


class AccountLockedException(BusinessLogicException):
    """Exception khi tài khoản bị khóa"""

    def __init__(self, message: str = "Account is locked", reason: str = None):
        super().__init__(
            message=message,
            error_code="ACCOUNT_LOCKED",
            details={"reason": reason}
        )


class AccountSuspendedException(BusinessLogicException):
    """Exception khi tài khoản bị tạm ngưng"""

    def __init__(self, message: str = "Account is suspended", reason: str = None, until: str = None):
        super().__init__(
            message=message,
            error_code="ACCOUNT_SUSPENDED",
            details={"reason": reason, "suspended_until": until}
        )


class InvalidOperationException(BusinessLogicException):
    """Exception khi thao tác không hợp lệ"""

    def __init__(self, message: str = "Invalid operation"):
        super().__init__(
            message=message,
            error_code="INVALID_OPERATION"
        )