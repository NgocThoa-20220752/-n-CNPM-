from pydantic import BaseModel

from app.enum.RoleEnum import RoleEnum
from app.enum.StatusAccountEnum import StatusAccountEnum
from datetime import datetime
from typing import Optional

from app.schemas.resp.UserResponse import UserResponse


class AccountResponse(BaseModel):
    id: int
    username: str
    role: RoleEnum
    status: StatusAccountEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Schema cho response token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginResponse(BaseModel):
    """Schema cho response đăng nhập"""
    success: bool = True
    message: str
    user: UserResponse
    tokens: TokenResponse


class RegisterResponse(BaseModel):
    """Schema cho response đăng ký"""
    success: bool = True
    message: str
    user: UserResponse
    requires_verification: bool = True
    verification_method: str


class PaginatedResponse(BaseModel):
    """Schema cho response phân trang"""
    success: bool = True
    data: list
    pagination: dict

    class Config:
        from_attributes = True


class SuccessResponse(BaseModel):
    """Schema cho response thành công"""
    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Schema cho response lỗi"""
    success: bool = False
    error: dict