from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_serializer
import uuid
from datetime import datetime
from typing import List
from books.schemas import Book

class UserCreate(BaseModel):
    # ✅ THE FIX: Prevent empty strings causing crashes
    username: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)

class UserLoginModel(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool
    role: str
    created_at: datetime
    books: List[Book] = [] 
    
    # ✅ THE FIX: Add "Z" here too
    @field_serializer('created_at')
    def serialize_dt(self, dt: datetime, _info):
        if dt.tzinfo is None:
            return dt.isoformat() + "Z"
        return dt.isoformat()

    class Config:
        from_attributes = True