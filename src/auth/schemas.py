from pydantic import BaseModel, EmailStr
import uuid
from datetime import datetime

# 1. Input Schema (What user sends)
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str

# 2. Output Schema (What we reply with)
# Notice: No password here. Includes UUID.
class UserResponse(BaseModel):
    uid: uuid.UUID 
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True