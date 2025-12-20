from sqlmodel import Session, create_engine, SQLModel
from config import Config

# Standard Synchronous Engine
engine = create_engine(
    url=Config.DATABASE_URL,
    echo=True
)

def init_db():
    from books.models import Book 
    SQLModel.metadata.create_all(bind=engine)

# ADD THIS: The session provider for your routes
def get_session():
    with Session(engine) as session:
        yield session # This "loans" the session to the route