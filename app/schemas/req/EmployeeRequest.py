from pydantic import BaseModel,Field, EmailStr, field_validator
from typing import Optional
from datetime import date

from app.enum import GenderEnum, RoleEnum, StatusAccountEnum


class CreateEmployeeRequest(BaseModel):
    """Schema cho tạo tài khoản nhân viên"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone_number: str = Field(..., min_length=10, max_length=20)
    dob: date
    gender: GenderEnum
    role: RoleEnum = Field(..., description="employee or admin")
    salary: Optional[float] = Field(None, ge=0, description="Salary for employee")
    hire_date: Optional[date] = Field(None, description="Hire date for employee")

    @field_validator('role')
    def validate_role(self, v):
        if v == RoleEnum.RoleEnum.CUSTOMER:
            raise ValueError('Cannot create customer account via this endpoint')
        return v

    @field_validator('salary')
    def validate_salary(self, v, values):
        if values.get('role') == RoleEnum.RoleEnum.EMPLOYEE and v is None:
            raise ValueError('Salary is required for employee')
        return v

    @field_validator('hire_date')
    def validate_hire_date(self, v, values):
        if values.get('role') == RoleEnum.RoleEnum.EMPLOYEE and v is None:
            raise ValueError('Hire date is required for employee')
        return v


class UpdateEmployeeRequest(BaseModel):
    """Schema cho cập nhật thông tin nhân viên"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, min_length=10, max_length=20)
    dob: Optional[date] = None
    gender: Optional[GenderEnum] = None
    salary: Optional[float] = Field(None, ge=0)
    status: Optional[StatusAccountEnum] = None


class SearchEmployeeRequest(BaseModel):
    """Schema cho tìm kiếm nhân viên"""
    keyword: Optional[str] = Field(None, description="Search by username, name, email")
    role: Optional[RoleEnum] = Field(None, description="Filter by role")
    status: Optional[StatusAccountEnum] = Field(None, description="Filter by status")
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)
