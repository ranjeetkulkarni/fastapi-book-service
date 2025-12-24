from pydantic import BaseModel, Field, ConfigDict, field_serializer # <--- Added field_serializer
from datetime import datetime
import uuid

class ReviewCreateModel(BaseModel):
    rating: int = Field(ge=1, le=5)
    review_text: str

class ReviewModel(BaseModel):
    uid: uuid.UUID
    rating: int
    review_text: str
    user_uid: uuid.UUID
    book_uid: uuid.UUID
    created_at: datetime
    updated_at: datetime

    # 1. UPDATED SERIALIZER
    @field_serializer('created_at', 'updated_at')
    def serialize_dt(self, dt: datetime, _info):
        if dt.tzinfo is None:
            return dt.isoformat() + "Z"
        return dt.isoformat()

    class Config:
        from_attributes = True