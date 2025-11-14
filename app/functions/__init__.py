"""
Core module - Chứa các cấu hình và tiện ích cơ bản
"""

from app.functions.PasswordHasher import PasswordHasher
from app.functions.JWTManager import jwt_manager, JWTManager
from app.functions.SecurityUtils import security_utils, SecurityUtils
from app.functions.Email import email_service, EmailService
from app.functions.SMS import sms_service, sms_verification_manager, SMSService
from app.functions.VerificationManager import verification_manager, VerificationManager

# Exception handler
from app.functions.ExceptionHandler import (
    ExceptionHandler,
    register_exception_handlers,
    handle_exceptions
)

# Exception middleware
from app.functions.ExceptionMiddleware import (
    ExceptionMiddleware,
    RequestLoggingMiddleware,
    CORSExceptionMiddleware
)

# Exception utilities
from app.functions.ExceptionUtils import (
    ExceptionUtils,
    exception_utils,
    try_except_wrapper,
    ErrorContext,
    validate_and_raise
)

__all__ = [

    # Security
    'PasswordHasher',
    'jwt_manager',
    'JWTManager',
    'security_utils',
    'SecurityUtils',

    # Services
    'email_service',
    'EmailService',
    'sms_service',
    'SMSService',
    'sms_verification_manager',

    # Verification
    'verification_manager',
    'VerificationManager',

    # Handler & Middleware
    'ExceptionHandler',
    'register_exception_handlers',
    'handle_exceptions',
    'ExceptionMiddleware',
    'RequestLoggingMiddleware',
    'CORSExceptionMiddleware',

    # Utils
    'ExceptionUtils',
    'exception_utils',
    'try_except_wrapper',
    'ErrorContext',
    'validate_and_raise',
]

