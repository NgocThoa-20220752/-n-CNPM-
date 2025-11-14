"""
Exception Handler
Xử lý và format exceptions thành response phù hợp
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from app.exception.BaseAPIException import BaseAPIException

logger = logging.getLogger(__name__)


class ExceptionHandler:
    """Class xử lý exceptions"""

    @staticmethod
    async def base_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
        """
        Handler cho BaseAPIException và các subclass

        Args:
            request: FastAPI request object
            exc: Exception instance

        Returns:
            JSONResponse với error details
        """
        logger.error(
            f"API Exception: {exc.error_code} - {exc.message}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status_code": exc.status_code,
                "details": exc.details
            }
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details
                }
            }
        )

    @staticmethod
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """
        Handler cho validation errors từ Pydantic

        Args:
            request: FastAPI request object
            exc: RequestValidationError instance

        Returns:
            JSONResponse với validation errors
        """
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"][1:]),
                "message": error["msg"],
                "type": error["type"]
            })

        logger.warning(
            f"Validation Error: {request.url.path}",
            extra={"errors": errors}
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Validation failed",
                    "details": {"errors": errors}
                }
            }
        )

    @staticmethod
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """
        Handler cho HTTP exceptions

        Args:
            request: FastAPI request object
            exc: HTTPException instance

        Returns:
            JSONResponse với error details
        """
        logger.warning(
            f"HTTP Exception: {exc.status_code} - {exc.detail}",
            extra={
                "path": request.url.path,
                "method": request.method
            }
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": exc.detail,
                    "details": {}
                }
            }
        )

    @staticmethod
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """
        Handler cho SQLAlchemy exceptions

        Args:
            request: FastAPI request object
            exc: SQLAlchemyError instance

        Returns:
            JSONResponse với error details
        """
        logger.error(
            f"Database Error: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method
            },
            exc_info=True
        )

        # Kiểm tra nếu là integrity error (duplicate, foreign key, etc.)
        if isinstance(exc, IntegrityError):
            error_message = "Database integrity constraint violation"
            if "Duplicate entry" in str(exc):
                error_message = "Record already exists"
            elif "foreign key constraint" in str(exc).lower():
                error_message = "Invalid reference to related record"
        else:
            error_message = "Database operation failed"

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": error_message,
                    "details": {}
                }
            }
        )

    @staticmethod
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Handler cho tất cả exceptions chưa được handle

        Args:
            request: FastAPI request object
            exc: Exception instance

        Returns:
            JSONResponse với generic error
        """
        logger.error(
            f"Unhandled Exception: {type(exc).__name__} - {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method
            },
            exc_info=True
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {}
                }
            }
        )


def register_exception_handlers(app):
    """
    Đăng ký tất cả exception handlers cho FastAPI app

    Args:
        app: FastAPI application instance
    """
    handler = ExceptionHandler()

    # Custom exceptions
    app.add_exception_handler(BaseAPIException, handler.base_exception_handler)

    # Validation errors
    app.add_exception_handler(RequestValidationError, handler.validation_exception_handler)

    # HTTP exceptions
    app.add_exception_handler(StarletteHTTPException, handler.http_exception_handler)

    # Database exceptions
    app.add_exception_handler(SQLAlchemyError, handler.sqlalchemy_exception_handler)

    # General exceptions (catch-all)
    app.add_exception_handler(Exception, handler.general_exception_handler)

    logger.info("Exception handlers registered successfully")


# Decorator để wrap functions với exception handling
def handle_exceptions(func):
    """
    Decorator để tự động xử lý exceptions

    Usage:
        @handle_exceptions
        def my_function():
            # Your code here
            pass
    """

    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except BaseAPIException:
            raise
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            raise BaseAPIException(
                message="An unexpected error occurred",
                error_code="INTERNAL_ERROR"
            )

    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BaseAPIException:
            raise
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            raise BaseAPIException(
                message="An unexpected error occurred",
                error_code="INTERNAL_ERROR"
            )

    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper