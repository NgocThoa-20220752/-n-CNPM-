from app.exception.BaseAPIException import BaseAPIException


class AuthorizationException(BaseAPIException):
    """Base exception cho authorization errors"""

    def __init__(self, message: str = "Authorization failed", **kwargs):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            **kwargs
        )


class PermissionDeniedException(AuthorizationException):
    """Exception khi không có permission"""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            error_code="PERMISSION_DENIED"
        )


class InsufficientPermissionsException(AuthorizationException):
    """Exception khi thiếu quyền cần thiết"""

    def __init__(self, message: str = "Insufficient permissions", required_permissions: list = None):
        super().__init__(
            message=message,
            error_code="INSUFFICIENT_PERMISSIONS",
            details={"required_permissions": required_permissions or []}
        )