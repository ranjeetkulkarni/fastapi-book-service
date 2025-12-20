from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime
import uuid

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
    # We use 'exclude=True' to prevent this field from appearing in JSON responses
    password_hash: str = Field(exclude=True, nullable=False)
    
    # 4. Status: Boolean flag for account verification
    is_verified: bool = Field(default=False)
    
    # 5. Audit: Timestamps using Postgres TIMESTAMP with Timezone
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.now)
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.now)
    )

    # Professional string representation for debugging
    def __repr__(self):
        return f"<User {self.username}>"