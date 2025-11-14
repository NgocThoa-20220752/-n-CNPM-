"""
Exception Utilities
Các tiện ích hỗ trợ exception handling
"""

import logging
from typing import Optional, Dict, Any, Callable
from functools import wraps
import traceback

from app.exception import (
    BaseAPIException,
    DatabaseException,
    ExternalServiceException
)

logger = logging.getLogger(__name__)


class ExceptionUtils:
    """Utilities cho exception handling"""

    @staticmethod
    def format_exception_message(exc: Exception, include_traceback: bool = False) -> str:
        """
        Format exception thành message dễ đọc

        Args:
            exc: Exception instance
            include_traceback: Có include traceback không

        Returns:
            Formatted message
        """
        message = f"{type(exc).__name__}: {str(exc)}"

        if include_traceback:
            tb = traceback.format_exc()
            message += f"\n\nTraceback:\n{tb}"

        return message

    @staticmethod
    def log_exception(
            exc: Exception,
            context: Optional[Dict[str, Any]] = None,
            level: str = "error"
    ):
        """
        Log exception với context

        Args:
            exc: Exception instance
            context: Additional context information
            level: Log level (error, warning, info)
        """
        log_func = getattr(logger, level.lower(), logger.error)

        log_func(
            f"Exception occurred: {type(exc).__name__} - {str(exc)}",
            extra={
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "context": context or {},
                "traceback": traceback.format_exc()
            },
            exc_info=True
        )

    @staticmethod
    def safe_execute(
            func: Callable,
            default_return: Any = None,
            exception_handler: Optional[Callable] = None,
            log_errors: bool = True
    ) -> Any:
        """
        Execute function an toàn, catch exceptions

        Args:
            func: Function cần execute
            default_return: Giá trị trả về mặc định nếu có lỗi
            exception_handler: Custom exception handler
            log_errors: Có log errors không

        Returns:
            Result của function hoặc default_return
        """
        try:
            return func()
        except Exception as exc:
            if log_errors:
                ExceptionUtils.log_exception(exc)

            if exception_handler:
                return exception_handler(exc)

            return default_return

    @staticmethod
    def wrap_database_exception(func):
        """
        Decorator để wrap database exceptions

        Usage:
            @wrap_database_exception
            def my_db_function():
                pass
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                logger.error(f"Database error in {func.__name__}: {str(exc)}")
                raise DatabaseException(
                    message=f"Database operation failed: {str(exc)}",
                    details={"function": func.__name__}
                )

        return wrapper

    @staticmethod
    def wrap_external_service_exception(service_name: str):
        """
        Decorator để wrap external service exceptions

        Usage:
            @wrap_external_service_exception("email")
            def send_email():
                pass
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    logger.error(f"External service error ({service_name}): {str(exc)}")
                    raise ExternalServiceException(
                        message=f"{service_name.capitalize()} service error: {str(exc)}",
                        service=service_name,
                        details={"function": func.__name__}
                    )

            return wrapper

        return decorator


def try_except_wrapper(
        default_return: Any = None,
        exceptions_to_catch: tuple = (Exception,),
        log_error: bool = True,
        raise_if_critical: bool = False
):
    """
    Decorator factory cho try-except wrapper

    Args:
        default_return: Giá trị trả về mặc định
        exceptions_to_catch: Tuple các exception cần catch
        log_error: Có log error không
        raise_if_critical: Có raise lại nếu là critical error

    Usage:
        @try_except_wrapper(default_return=[], exceptions_to_catch=(ValueError,))
        def my_function():
            pass
    """

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except exceptions_to_catch as exc:
                if log_error:
                    ExceptionUtils.log_exception(exc, context={
                        "function": func.__name__,
                        "args": str(args)[:100],
                        "kwargs": str(kwargs)[:100]
                    })

                if raise_if_critical and isinstance(exc, BaseAPIException):
                    raise

                return default_return

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions_to_catch as exc:
                if log_error:
                    ExceptionUtils.log_exception(exc, context={
                        "function": func.__name__,
                        "args": str(args)[:100],
                        "kwargs": str(kwargs)[:100]
                    })

                if raise_if_critical and isinstance(exc, BaseAPIException):
                    raise

                return default_return

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class ErrorContext:
    """
    Context manager để xử lý errors trong một block code

    Usage:
        with ErrorContext("processing user data", user_id=123):
            # Your code here
            process_user()
    """

    def __init__(
            self,
            operation: str,
            raise_exception: bool = True,
            default_return: Any = None,
            **context
    ):
        self.operation = operation
        self.raise_exception = raise_exception
        self.default_return = default_return
        self.context = context
        self.exception = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.exception = exc_val

            # Log error với context
            logger.error(
                f"Error during {self.operation}: {exc_val}",
                extra={
                    "operation": self.operation,
                    "context": self.context,
                    "exception_type": exc_type.__name__,
                    "traceback": traceback.format_exc()
                },
                exc_info=True
            )

            # Không raise exception nếu raise_exception = False
            if not self.raise_exception:
                return True  # Suppress exception

        return False  # Propagate exception


def validate_and_raise(
        condition: bool,
        exception: BaseAPIException,
        log_warning: bool = True
):
    """
    Validate điều kiện và raise exception nếu không đúng

    Args:
        condition: Điều kiện cần check
        exception: Exception cần raise
        log_warning: Có log warning không

    Usage:
        validate_and_raise(
            user is not None,
            NotFoundException("User not found")
        )
    """
    if not condition:
        if log_warning:
            logger.warning(
                f"Validation failed: {exception.message}",
                extra={
                    "error_code": exception.error_code,
                    "details": exception.details
                }
            )
        raise exception


# Singleton instance
exception_utils = ExceptionUtils()