from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime
import uuid
from typing import List, Optional

# Link to other models (Forward reference to avoid circular imports)
# Make sure your Book and Review models are imported or available if they are in the same file
# from books.models import Book 
# from reviews.models import Review

class User(SQLModel, table=True):
    __tablename__ = 'users'
    
    # 1. Primary Key: Using PostgreSQL UUID for distributed safety
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    
    # 2. Identification: Indexed for fast login lookups
    username: str = Field(unique=True, index=True, nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    
    # 3. Security: Storing hash, NOT plain text
    password_hash: str = Field(exclude=True, nullable=False)
    
    # 4. Status: Boolean flag for account verification
    is_verified: bool = Field(default=False)
    
    # 5. Roles: Authorization Level (New Field)
    # server_default ensures the database sets 'user' if we forget to send it
    role: str = Field(
        sa_column=Column(
            pg.VARCHAR, 
            nullable=False, 
            server_default="user"
        )
    )

    # 6. Audit: Timestamps using Postgres TIMESTAMP with Timezone
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.now)
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.now)
    )

    # 7. Relationships (Crucial for "My Books" feature)
    # These link the User table to the Book and Review tables
    books: List["Book"] = Relationship(back_populates="user")
    reviews: List["Review"] = Relationship(back_populates="user")

    # Professional string representation for debugging
    def __repr__(self):
        return f"<User {self.username}>"