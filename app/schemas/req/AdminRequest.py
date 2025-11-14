from pydantic import BaseModel,Field

class AdminRequest(BaseModel):
    admin_id: str = Field(..., max_length=50)
    user_id: int


