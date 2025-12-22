from pydantic import BaseModel, EmailStr
import uuid
from datetime import datetime
from typing import List  # <--- FIXED: Import List here
from books.schemas import Book  # <--- FIXED: Import Book schema here

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str

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
    
    # This now works because 'List' and 'Book' are imported above
    books: List[Book] = [] 
    
    class Config:
        from_attributes = True