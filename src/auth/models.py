from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime
import uuid
from typing import List, Optional

# Forward references (strings) prevent circular import errors
# if TYPE_CHECKING:
#     from books.models import Book
#     from reviews.models import Review

class User(SQLModel, table=True):
    __tablename__ = 'users'
    
    # 1. Primary Key
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    
    # 2. Identification
    username: str = Field(unique=True, index=True, nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    
    # 3. Security
    password_hash: str = Field(exclude=True, nullable=False)
    
    # 4. Status
    is_verified: bool = Field(default=False)
    
    # 5. Roles
    role: str = Field(
        sa_column=Column(
            pg.VARCHAR, 
            nullable=False, 
            server_default="user"
        )
    )

    # 6. Audit
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.now)
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.now)
    )

    # 7. Relationships (The Placement Topic: Selectin Loading)
    # "lazy": "selectin" -> Eagerly loads books when you fetch the user.
    # Without this, accessing user.books in async code will throw an error or cause lag.
    books: List["Book"] = Relationship(
        back_populates="user", 
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    
    # reviews: List["Review"] = Relationship(
    #     back_populates="user",
    #     sa_relationship_kwargs={"lazy": "selectin"}
    # )

    def __repr__(self):
        return f"<User {self.username}>"