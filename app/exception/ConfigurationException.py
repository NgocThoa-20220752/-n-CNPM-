from app.exception.BaseAPIException import BaseAPIException


class ConfigurationException(BaseAPIException):
    """Exception khi có lỗi cấu hình"""

    def __init__(self, message: str = "Configuration error", config_key: str = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="CONFIGURATION_ERROR",
            details={"config_key": config_key}
        )