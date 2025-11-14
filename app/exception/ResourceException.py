from app.exception.BaseAPIException import BaseAPIException


class ResourceException(BaseAPIException):
    """Base exception cho resource errors"""

    def __init__(self, message: str = "Resource error", **kwargs):
        super().__init__(
            message=message,
            status_code=404,
            error_code="RESOURCE_ERROR",
            **kwargs
        )


class NotFoundException(ResourceException):
    """Exception khi không tìm thấy resource"""

    def __init__(self, message: str = "Resource not found", resource: str = None, resource_id: str = None):
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            details={"resource": resource, "resource_id": resource_id}
        )


class AlreadyExistsException(BaseAPIException):
    """Exception khi resource đã tồn tại"""

    def __init__(self, message: str = "Resource already exists", resource: str = None):
        super().__init__(
            message=message,
            status_code=409,
            error_code="ALREADY_EXISTS",
            details={"resource": resource}
        )


class DuplicateEmailException(AlreadyExistsException):
    """Exception khi email đã tồn tại"""

    def __init__(self, email: str = None):
        super().__init__(
            message=f"Email {email} already exists" if email else "Email already exists",
            resource="email"
        )


class DuplicatePhoneException(AlreadyExistsException):
    """Exception khi số điện thoại đã tồn tại"""

    def __init__(self, phone: str = None):
        super().__init__(
            message=f"Phone {phone} already exists" if phone else "Phone already exists",
            resource="phone"
        )