from app.exception.BaseAPIException import BaseAPIException


class DatabaseException(BaseAPIException):
    """Base exception cho database errors"""

    def __init__(self, message: str = "Database error", **kwargs):
        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR",
            **kwargs
        )


class DatabaseConnectionException(DatabaseException):
    """Exception khi không kết nối được database"""

    def __init__(self, message: str = "Database connection failed"):
        super().__init__(
            message=message,
            error_code="DB_CONNECTION_ERROR"
        )


class DatabaseQueryException(DatabaseException):
    """Exception khi query database thất bại"""

    def __init__(self, message: str = "Database query failed", query: str = None):
        super().__init__(
            message=message,
            error_code="DB_QUERY_ERROR",
            details={"query": query}
        )