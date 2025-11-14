from pydantic import BaseModel,Field,EmailStr
from datetime import date
from typing import Optional

from app.enum.GenderEnum import GenderEnum


class UserRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    dob: date
    phone_number: str = Field(..., min_length=10, max_length=20)
    email: EmailStr
    gender: GenderEnum

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    dob: Optional[date] = None
    phone_number: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    gender: Optional[GenderEnum] = None