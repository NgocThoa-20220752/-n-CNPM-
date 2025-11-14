from app.exception.BaseAPIException import BaseAPIException


class FileUploadException(BaseAPIException):
    """Base exception cho file upload errors"""

    def __init__(self, message: str = "File upload error", **kwargs):
        super().__init__(
            message=message,
            status_code=400,
            error_code="FILE_UPLOAD_ERROR",
            **kwargs
        )


class FileSizeExceededException(FileUploadException):
    """Exception khi file quá lớn"""

    def __init__(self, message: str = "File size exceeded", max_size: int = None):
        super().__init__(
            message=message,
            error_code="FILE_SIZE_EXCEEDED",
            details={"max_size": max_size}
        )


class InvalidFileTypeException(FileUploadException):
    """Exception khi file type không hợp lệ"""

    def __init__(self, message: str = "Invalid file type", allowed_types: list = None):
        super().__init__(
            message=message,
            error_code="INVALID_FILE_TYPE",
            details={"allowed_types": allowed_types or []}
        )