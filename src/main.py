from fastapi import FastAPI
from books.routes import book_router
from auth.routes import router as auth_router
from reviews.routes import review_router
# 1. IMPORT REGISTRATION FUNCTION
from errors import register_all_errors

app = FastAPI(
    title="Bookly",
    description="A REST API for a Book Review Service",
    version="v1"
)

# 2. REGISTER HANDLERS HERE
register_all_errors(app)

app.include_router(book_router, prefix="/api/v1/books", tags=['books'])
app.include_router(auth_router, prefix="/api/v1/auth", tags=['auth'])
app.include_router(review_router, prefix="/api/v1/reviews", tags=['reviews'])