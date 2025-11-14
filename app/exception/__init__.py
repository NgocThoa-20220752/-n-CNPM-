"""
Exception Module
Quản lý tất cả exceptions và error handling
"""

# Base exception
from app.exception.BaseAPIException import BaseAPIException

# Authentication exceptions
from app.exception.AuthenticationException import (
    AuthenticationException,
    InvalidCredentialsException,
    TokenExpiredException,
    InvalidTokenException,
    UnauthorizedException
)

# Authorization exceptions
from app.exception.AuthorizationException import (
    AuthorizationException,
    PermissionDeniedException,
    InsufficientPermissionsException
)

# Validation exceptions
from app.exception.ValidationException import (
    ValidationException,
    InvalidInputException,
    WeakPasswordException,
    InvalidEmailException,
    InvalidPhoneException
)

# Resource exceptions
from app.exception.ResourceException import (
    ResourceException,
    NotFoundException,
    AlreadyExistsException,
    DuplicateEmailException,
    DuplicatePhoneException
)

# Database exceptions
from app.exception.DatabaseException import (
    DatabaseException,
    DatabaseConnectionException,
    DatabaseQueryException
)

# Rate limiting exceptions
from app.exception.RateLimitException import (
    RateLimitException,
    TooManyRequestsException,
    VerificationAttemptsExceededException
)

# Verification exceptions
from app.exception.VerificationException import (
    VerificationException,
    InvalidVerificationCodeException,
    VerificationCodeExpiredException,
    VerificationNotFoundException
)

# External service exceptions
from app.exception.ExternalServiceException import (
    ExternalServiceException,
    EmailServiceException,
    SMSServiceException
)

# Business logic exceptions
from app.exception.BusinessLogicException import (
    BusinessLogicException,
    AccountNotActiveException,
    AccountLockedException,
    AccountSuspendedException,
    InvalidOperationException
)

# File upload exceptions
from app.exception.FileUploadException import (
    FileUploadException,
    FileSizeExceededException,
    InvalidFileTypeException
)

# Configuration exception
from app.exception.ConfigurationException import ConfigurationException


__all__ = [
    # Base
    'BaseAPIException',

    # Authentication
    'AuthenticationException',
    'InvalidCredentialsException',
    'TokenExpiredException',
    'InvalidTokenException',
    'UnauthorizedException',

    # Authorization
    'AuthorizationException',
    'PermissionDeniedException',
    'InsufficientPermissionsException',

    # Validation
    'ValidationException',
    'InvalidInputException',
    'WeakPasswordException',
    'InvalidEmailException',
    'InvalidPhoneException',

    # Resource
    'ResourceException',
    'NotFoundException',
    'AlreadyExistsException',
    'DuplicateEmailException',
    'DuplicatePhoneException',

    # Database
    'DatabaseException',
    'DatabaseConnectionException',
    'DatabaseQueryException',

    # Rate Limiting
    'RateLimitException',
    'TooManyRequestsException',
    'VerificationAttemptsExceededException',

    # Verification
    'VerificationException',
    'InvalidVerificationCodeException',
    'VerificationCodeExpiredException',
    'VerificationNotFoundException',

    # External Services
    'ExternalServiceException',
    'EmailServiceException',
    'SMSServiceException',

    # Business Logic
    'BusinessLogicException',
    'AccountNotActiveException',
    'AccountLockedException',
    'AccountSuspendedException',
    'InvalidOperationException',

    # File Upload
    'FileUploadException',
    'FileSizeExceededException',
    'InvalidFileTypeException',

    # Configuration
    'ConfigurationException',
]