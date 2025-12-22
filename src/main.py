from fastapi import FastAPI
from books.routes import book_router
from auth.routes import router as auth_router
from reviews.routes import review_router # <--- Import this

app = FastAPI(
    title="Bookly",
    description="A REST API for a Book Review Service",
    version="v1"
)

# 1. Register the Books Router
app.include_router(
    book_router, 
    prefix="/api/v1/books", 
    tags=['books']
)

# 2. Register the Auth Router
app.include_router(
    auth_router, 
    prefix="/api/v1/auth", 
    tags=['auth']
)

app.include_router(
    review_router,
    prefix="/api/v1/reviews", 
    tags=['reviews']
    )