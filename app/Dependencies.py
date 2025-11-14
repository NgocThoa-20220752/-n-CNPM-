"""
Authentication & Authorization Dependencies
Sử dụng trong FastAPI Depends
"""

from fastapi import Depends, Header
from jwt import PyJWTError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import Optional

from app.models.Users import Users
from app.enum.RoleEnum import RoleEnum
from app.enum.StatusAccountEnum import StatusAccountEnum
from core import get_db
from core.security import jwt_manager
from exception import UnauthorizedException, TokenExpiredException, InvalidTokenException, AccountNotActiveException, \
    PermissionDeniedException


def get_token_from_header(authorization: Optional[str] = Header(None)) -> str:
    """
    Extract JWT token từ Authorization header

    Args:
        authorization: Authorization header (Bearer <token>)

    Returns:
        JWT token string
    """
    if not authorization:
        raise UnauthorizedException("Authorization header missing")

    if not authorization.startswith("Bearer "):
        raise UnauthorizedException("Invalid authorization format. Use 'Bearer <token>'")

    token = authorization.replace("Bearer ", "")

    if not token:
        raise UnauthorizedException("Token is empty")

    return token


def get_current_user(
        token: str = Depends(get_token_from_header),
        db: Session = Depends(get_db)
) -> Optional[Users]:
    """
    Lấy user hiện tại từ JWT token

    Args:
        token: JWT access token
        db: Database session

    Returns:
        Users object
    """
    # Verify token
    payload = jwt_manager.verify_token(token, token_type="access")

    if not payload:
        raise TokenExpiredException("Access token has expired or invalid")

    # Get user_id from payload
    user_id = payload.get("user_id")

    if not user_id:
        raise InvalidTokenException("Invalid token payload")

    # Get user from database
    user = db.query(Users).filter_by(id=user_id).first()

    if not user or not user.account:
        raise UnauthorizedException("User not found or account invalid")

    # Check account status
    account = user.account

    if account.status == StatusAccountEnum.INACTIVE:
        raise AccountNotActiveException(
            "Account is not active. Please verify your account."
        )
    elif account.status == StatusAccountEnum.LOCKED:
        from app.exception import AccountLockedException
        raise AccountLockedException(
            message="Account has been locked",
            reason="Security violation"
        )
    elif account.status == StatusAccountEnum.SUSPENDED:
        from app.exception import AccountSuspendedException
        raise AccountSuspendedException(
            message="Account has been suspended",
            reason="Policy violation"
        )

    return user


def require_role(required_role: RoleEnum):
    """
    Factory function tạo dependency kiểm tra role

    Usage:
        @app.get("/admin/dashboard", dependencies=[Depends(require_role(RoleEnum.ADMIN))])
    """

    def check_role(current_user: Users = Depends(get_current_user)) -> Users:
        if current_user.account.role != required_role:
            raise PermissionDeniedException(
                f"This endpoint requires {required_role.value} role"
            )
        return current_user

    return check_role


def require_roles(*roles: RoleEnum):
    """
    Factory function tạo dependency kiểm tra nhiều roles

    Usage:
        @app.get("/dashboard", dependencies=[Depends(require_roles(RoleEnum.ADMIN, RoleEnum.EMPLOYEE))])
    """

    def check_roles(current_user: Users = Depends(get_current_user)) -> Users:
        if current_user.account.role not in roles:
            roles_str = ", ".join([r.value for r in roles])
            raise PermissionDeniedException(
                f"This endpoint requires one of these roles: {roles_str}"
            )
        return current_user

    return check_roles


# Predefined dependencies cho các roles thường dùng

def require_admin(current_user: Users = Depends(get_current_user)) -> Users:
    """
    Yêu cầu role ADMIN
    """
    if current_user.account.role != RoleEnum.ADMIN:
        raise PermissionDeniedException("This endpoint requires admin role")
    return current_user


def require_employee(current_user: Users = Depends(get_current_user)) -> Users:
    """
    Yêu cầu role EMPLOYEE
    """
    if current_user.account.role != RoleEnum.EMPLOYEE:
        raise PermissionDeniedException("This endpoint requires employee role")
    return current_user


def require_customer(current_user: Users = Depends(get_current_user)) -> Users:
    """
    Yêu cầu role CUSTOMER
    """
    if current_user.account.role != RoleEnum.CUSTOMER:
        raise PermissionDeniedException("This endpoint requires customer role")
    return current_user


def require_admin_or_employee(current_user: Users = Depends(get_current_user)) -> Users:
    """
    Yêu cầu role ADMIN hoặc EMPLOYEE
    """
    if current_user.account.role not in [RoleEnum.ADMIN, RoleEnum.EMPLOYEE]:
        raise PermissionDeniedException(
            "This endpoint requires admin or employee role"
        )
    return current_user


def get_optional_user(
        authorization: Optional[str] = Header(None),
        db: Session = Depends(get_db)
) -> Optional[Users]:
    """
    Lấy user nếu có token, None nếu không có.
    Sử dụng cho endpoints không bắt buộc đăng nhập.
    """
    if not authorization:
        return None

    token = authorization.replace("Bearer ", "")

    try:
        payload = jwt_manager.verify_token(token, token_type="access")
    except PyJWTError:
        return None  # JWT invalid hoặc expired

    if not payload:
        return None

    user_id = payload.get("user_id")
    if not user_id:
        return None

    try:
        user = db.query(Users).filter_by(id=user_id).first()
    except SQLAlchemyError:
        return None  # lỗi database

    if not user or not user.account:
        return None

    if user.account.status != StatusAccountEnum.ACTIVE:
        return None

    return user


# Dependency kiểm tra quyền sở hữu resource
def require_owner_or_admin(resource_user_id: int):
    """
    Kiểm tra user là owner của resource hoặc là admin

    Usage:
        @app.put("/users/{user_id}")
        async def update_user(
            user_id: int,
            current_user: Users = Depends(require_owner_or_admin(user_id))
        ):
            pass
    """

    def check_ownership(current_user: Users = Depends(get_current_user)) -> Users:
        is_owner = current_user.id == resource_user_id
        is_admin = current_user.account.role == RoleEnum.ADMIN

        if not (is_owner or is_admin):
            raise PermissionDeniedException(
                "You don't have permission to access this resource"
            )

        return current_user

    return check_ownership