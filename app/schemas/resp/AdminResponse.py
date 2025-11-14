from pydantic import BaseModel

from app.schemas.resp.UserResponse import UserResponse


class AdminResponse(BaseModel):
    admin_id: str
    user: UserResponse

    class Config:
        from_attributes = True
