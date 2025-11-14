from pydantic import BaseModel

from app.schemas.resp.UserResponse import UserResponse


class CustomerResponse(BaseModel):
    """Schema cho thông tin khách hàng"""
    customer_id: str
    user: UserResponse

    class Config:
        from_attributes = True