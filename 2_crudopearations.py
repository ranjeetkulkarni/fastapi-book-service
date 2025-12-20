from typing import Annotated
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI()

# --- TASK 1 MODELS & ROUTES ---
class Book(BaseModel):
    title: str
    author: str

@app.get("/greet/{name}")
async def greet_user(name: str):
    return {"message": f"Hello, {name}!"}

@app.get("/get-headers")
async def read_headers(
    user_agent: Annotated[str | None, Header()] = None,
    custom_secret: Annotated[str | None, Header()] = None
):
    return {"detected_browser": user_agent, "your_custom_header": custom_secret}

# --- TASK 2: CRUD LOGIC WITH SEEDED DATA ---

class BookCRUD(BaseModel):
    id: int
    title: str
    author: str

# Pre-populating the list so it's not empty on startup
db = [
    {"id": 1, "title": "Deep Work", "author": "Cal Newport"},
    {"id": 2, "title": "Atomic Habits", "author": "James Clear"},
    {"id": 3, "title": "The Alchemist", "author": "Paulo Coelho"}
]

# GET: List all books
@app.get("/books")
async def get_all_books():
    return {"total_books": len(db), "data": db}

# POST: Create a book
@app.post("/books")
async def create_book_crud(book: BookCRUD):
    db.append(book.dict())
    return {"message": "Book added to DB", "book": book}

# PATCH: Update a specific book's title
@app.patch("/book/{book_id}")
async def update_book(book_id: int, new_title: str):
    for book in db:
        if book["id"] == book_id:
            book["title"] = new_title
            return {"message": "Update successful", "updated_book": book}
    raise HTTPException(status_code=404, detail="Book ID not found")

# DELETE: Remove a book
@app.delete("/book/{book_id}")
async def delete_book(book_id: int):
    global db
    initial_length = len(db)
    db = [book for book in db if book["id"] != book_id]
    
    if len(db) == initial_length:
        raise HTTPException(status_code=404, detail="Book not found")
        
    return {"message": f"Book {book_id} deleted"}