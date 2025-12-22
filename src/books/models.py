from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column # <--- Import Column explicitly
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime, date
import uuid
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from auth.models import User

class Book(SQLModel, table=True):
    __tablename__ = "books"
    
    uid: uuid.UUID = Field(
        sa_column=Column( # <--- Use 'Column', NOT 'pg.Column'
            pg.UUID, 
            nullable=False, 
            primary_key=True, 
            default=uuid.uuid4
        )
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    
    # Timestamps
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.now)
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.now)
    )

    # --- FOREIGN KEY ---
    user_uid: Optional[uuid.UUID] = Field(
        default=None, 
        foreign_key="users.uid" # Links to User table
    )

    # --- RELATIONSHIP ---
    user: Optional["User"] = Relationship(back_populates="books")

    def __repr__(self):
        return f"<Book {self.title}>"