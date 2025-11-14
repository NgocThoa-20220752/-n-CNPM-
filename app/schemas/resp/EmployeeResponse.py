from pydantic import BaseModel
from typing import Optional
from datetime import date

from app.schemas.resp.UserResponse import UserResponse


class EmployeeResponse(BaseModel):
    """Schema cho thông tin nhân viên"""
    employee_id: str
    user: UserResponse
    salary: Optional[float]
    hire_date: Optional[date]

    class Config:
        from_attributes = True