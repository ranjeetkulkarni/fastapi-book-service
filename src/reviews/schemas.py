from pydantic import BaseModel, Field
from datetime import datetime
import uuid

# 1. Incoming Data (What the user sends)
class ReviewCreateModel(BaseModel):
    rating: int = Field(ge=1, le=5) # Enforce 1-5 stars
    review_text: str

# 2. Outgoing Data (What we send back)
class ReviewModel(BaseModel):
    uid: uuid.UUID
    rating: int
    review_text: str
    user_uid: uuid.UUID
    book_uid: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True