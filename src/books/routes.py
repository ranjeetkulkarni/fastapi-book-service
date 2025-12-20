from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from typing import List
from db.main import get_session
from .service import BookService
from .schemas import Book, BookCreateModel, BookUpdateModel

book_router = APIRouter()
book_service = BookService() # Our "Librarian" class

@book_router.get("/", response_model=List[Book])
async def get_all_books(session: Session = Depends(get_session)):
    # Service handles the SQL; Route handles the response
    return book_service.get_all_books(session)

@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_book(book_data: BookCreateModel, session: Session = Depends(get_session)):
    return book_service.create_book(book_data, session)

@book_router.get("/{book_uid}", response_model=Book)
async def get_book(book_uid: str, session: Session = Depends(get_session)):
    book = book_service.get_book(book_uid, session)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@book_router.patch("/{book_uid}", response_model=Book)
async def update_book(book_uid: str, update_data: BookUpdateModel, session: Session = Depends(get_session)):
    updated_book = book_service.update_book(book_uid, update_data, session)
    if not updated_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated_book

@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_uid: str, session: Session = Depends(get_session)):
    deleted = book_service.delete_book(book_uid, session)
    if not deleted:
        raise HTTPException(status_code=404, detail="Book not found")
    return None