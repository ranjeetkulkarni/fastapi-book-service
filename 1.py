from typing import Annotated
from fastapi import FastAPI, Header
from pydantic import BaseModel

app = FastAPI()

class Book(BaseModel):
    title: str
    author: str

# 1. Path Parameter Route
@app.get("/greet/{name}")
async def greet_user(name: str):
    return {"message": f"Hello, {name}!"}

# 2. POST Route (Pydantic Body)
@app.post("/books/")
async def create_book(book: Book):
    return {"status": "success", "received_book": book}

# 3. NEW: Headers Route
@app.get("/get-headers")
async def read_headers(
    user_agent: Annotated[str | None, Header()] = None,
    custom_secret: Annotated[str | None, Header()] = None
):
    """
    FastAPI automatically converts 'Custom-Secret' in Postman 
    to 'custom_secret' here.
    """
    return {
        "detected_browser": user_agent,
        "your_custom_header": custom_secret,
        "note": "Check the Headers tab in Postman to send these!"
    }