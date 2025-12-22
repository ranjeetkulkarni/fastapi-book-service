from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date # <--- Import date
import uuid
from typing import List # <--- Import List
from reviews.schemas import ReviewModel # <--- Import Review Schema

# 1. Ensure this is 'BookCreateModel' to match your imports
class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str

# 2. This is the main schema used for responses
class Book(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    # 1. FIX TYPE: Change 'str' to 'date'
    published_date: date 
    page_count: int
    language: str
    created_at: datetime
    # 2. FIX TYPO: Change 'update_at' to 'updated_at'
    updated_at: datetime 

    class Config:
        from_attributes = True

# 3. Ensure this is 'BookUpdateModel'
class BookUpdateModel(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[str] = None
    page_count: Optional[int] = None
    language: Optional[str] = None

class BookDetailModel(Book):
    reviews: List[ReviewModel]