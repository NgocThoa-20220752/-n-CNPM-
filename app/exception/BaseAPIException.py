class BaseAPIException(Exception):
    """Base exception class cho tất cả API exceptions"""

    def __init__(
            self,
            message: str = "An error occurred",
            status_code: int = 500,
            error_code: str = "INTERNAL_ERROR",
            details: dict = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self):
        """Convert exception to dictionary"""
        return {
            "error": self.error_code,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details
        }