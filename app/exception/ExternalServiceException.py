from app.exception.BaseAPIException import BaseAPIException


class ExternalServiceException(BaseAPIException):
    """Base exception cho external service errors"""

    def __init__(self, message: str = "External service error", service: str = None, **kwargs):
        super().__init__(message)  # chỉ truyền message
        self.status_code = 503
        self.error_code = "EXTERNAL_SERVICE_ERROR"
        self.details = {"service": service}
        self.extra = kwargs  # nếu muốn lưu các thông tin thêm

class EmailServiceException(ExternalServiceException):
    """Exception khi email service lỗi"""

    def __init__(self, message: str = "Email service error"):
        super().__init__(
            message=message,
            service="email",
            error_code="EMAIL_SERVICE_ERROR"
        )


class SMSServiceException(ExternalServiceException):
    """Exception khi SMS service lỗi"""

    def __init__(self, message: str = "SMS service error"):
        super().__init__(
            message=message,
            service="sms",
            error_code="SMS_SERVICE_ERROR"
        )
