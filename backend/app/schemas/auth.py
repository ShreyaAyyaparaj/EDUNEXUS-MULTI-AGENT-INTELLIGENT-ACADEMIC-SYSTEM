from pydantic import BaseModel
from typing import Optional
from app.models.all_models import UserRole

class LoginRequest(BaseModel):
    username_or_email: str
    password: str
    selected_role: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    full_name: str
    email: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    department_id: Optional[int] = None

    class Config:
        from_attributes = True
