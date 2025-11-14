from pydantic import BaseModel
from datetime import datetime
from datetime import date


class UserResponse(BaseModel):
    """Schema cho thông tin user"""
    id: int
    username: str
    full_name: str
    email: str
    phone_number: str
    dob: date
    gender: str
    role: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True