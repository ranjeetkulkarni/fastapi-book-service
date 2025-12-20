from fastapi import FastAPI
from contextlib import asynccontextmanager
from books.routes import book_router
from db.main import init_db

@asynccontextmanager
async def life_span(app: FastAPI):
    print("Connecting to Neon...")
    # FIX: Remove 'await' because init_db is now synchronous
    init_db() 
    yield
    print("Closing connections...")

app = FastAPI(
    title="Bookly",
    lifespan=life_span
)

app.include_router(book_router, prefix="/api/v1/books", tags=['books'])