from pydantic import BaseModel, Field,EmailStr
from datetime import date
from typing import Optional

from app.enum import StatusAccountEnum, GenderEnum

class UpdateCustomerStatusRequest(BaseModel):
    """Schema cho cập nhật trạng thái khách hàng"""
    status: StatusAccountEnum = Field(..., description="New status")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for status change")


class SearchCustomerRequest(BaseModel):
    """Schema cho tìm kiếm khách hàng"""
    keyword: Optional[str] = Field(None, description="Search by username, name, email, phone")
    status: Optional[StatusAccountEnum] = Field(None, description="Filter by status")
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)


class UpdateProfileRequest(BaseModel):
    """Schema cho khách hàng cập nhật thông tin cá nhân"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone_number: Optional[str] = Field(None, min_length=10, max_length=20)
    dob: Optional[date] = None
    gender: Optional[GenderEnum] = None
    email: Optional[EmailStr] = None