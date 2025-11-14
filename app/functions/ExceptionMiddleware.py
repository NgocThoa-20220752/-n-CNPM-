"""
Exception Middleware
Middleware để catch và xử lý exceptions toàn cục
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging
import time
import traceback
from typing import Callable

from app.exception.BaseAPIException import BaseAPIException

logger = logging.getLogger(__name__)


class ExceptionMiddleware(BaseHTTPMiddleware):
    """
    Middleware để handle exceptions và log requests
    """

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Process request và handle exceptions

        Args:
            request: Request object
            call_next: Next middleware/handler

        Returns:
            Response object
        """
        start_time = time.time()
        request_id = self._generate_request_id()

        # Add request_id to request state
        request.state.request_id = request_id

        try:
            # Log incoming request
            logger.info(
                f"Request started: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": str(request.query_params),
                    "client_host": request.client.host if request.client else None
                }
            )

            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{duration:.4f}"

            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "duration": duration
                }
            )

            return response

        except BaseAPIException as exc:
            # Handle custom exceptions
            duration = time.time() - start_time

            logger.error(
                f"API Exception: {exc.error_code}",
                extra={
                    "request_id": request_id,
                    "error_code": exc.error_code,
                    "message": exc.message,
                    "status_code": exc.status_code,
                    "duration": duration
                }
            )

            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "request_id": request_id,
                    "error": {
                        "code": exc.error_code,
                        "message": exc.message,
                        "details": exc.details
                    }
                },
                headers={"X-Request-ID": request_id}
            )

        except Exception as exc:
            # Handle unexpected exceptions
            duration = time.time() - start_time

            logger.error(
                f"Unhandled Exception: {type(exc).__name__}",
                extra={
                    "request_id": request_id,
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                    "duration": duration
                },
                exc_info=True
            )

            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "request_id": request_id,
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected error occurred",
                        "details": {}
                    }
                },
                headers={"X-Request-ID": request_id}
            )

    @staticmethod
    def _generate_request_id() -> str:
        """Generate unique request ID"""
        import uuid
        return str(uuid.uuid4())


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware để log chi tiết requests/responses
    """

    async def dispatch(self, request: Request, call_next: Callable):
        """Log request and response details"""

        # Chỉ log body cho POST/PUT/PATCH
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                # Không log các endpoint nhạy cảm
                sensitive_paths = ["/auth/login", "/auth/register", "/auth/reset-password"]
                if request.url.path not in sensitive_paths:
                    try:
                        body_str = body_bytes.decode('utf-8')
                        logger.debug(
                            f"Request body: {body_str[:1000]}",  # giới hạn 1000 ký tự
                            extra={"path": request.url.path}
                        )
                    except UnicodeDecodeError as e:
                        logger.warning(f"Cannot decode request body for {request.url.path}: {e}")
            except Exception as e:
                logger.warning(f"Failed to read request body for {request.url.path}: {e}")

        response = await call_next(request)
        return response


class CORSExceptionMiddleware(BaseHTTPMiddleware):
    """
    Middleware để handle CORS cho exception responses
    """

    async def dispatch(self, request: Request, call_next: Callable):
        """Ensure CORS headers on error responses"""
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            # Re-raise to be caught by other middleware
            raise exc