from fastapi import FastAPI
from contextlib import asynccontextmanager
from books.routes import book_router
from auth.routes import router as auth_router # <--- 1. Import the Auth Router
from db.main import init_db

@asynccontextmanager
async def life_span(app: FastAPI):
    print("Connecting to Neon (via SQLModel)...")
    # init_db is synchronous, so we call it directly (no await)
    # This creates tables if they don't exist
    init_db() 
    yield
    print("Closing connections...")

app = FastAPI(
    title="Bookly",
    description="A REST API for a Book Review Service",
    version="v1",
    lifespan=life_span
)

# 2. Register the Books Router
app.include_router(
    book_router, 
    prefix="/api/v1/books", 
    tags=['books']
)

# 3. Register the Auth Router
# This creates endpoints like: POST /api/v1/auth/signup
app.include_router(
    auth_router, 
    prefix="/api/v1/auth", 
    tags=['auth']
)