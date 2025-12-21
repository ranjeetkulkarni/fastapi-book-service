from pydantic import BaseModel, EmailStr
import uuid
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str

# --- NEW: Login Schema ---
class UserLoginModel(BaseModel):
    email: EmailStr
    password: str

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