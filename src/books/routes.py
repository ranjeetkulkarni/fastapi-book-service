from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from typing import List
from db.main import get_session
from .service import BookService
from .schemas import Book, BookCreateModel, BookUpdateModel
# --- NEW IMPORT ---
from auth.dependencies import AccessTokenBearer 

book_router = APIRouter()
book_service = BookService() 
access_token_bearer = AccessTokenBearer() # Initialize the "Gatekeeper"

# 1. Public Route (Anyone can read)
@book_router.get("/", response_model=List[Book])
def get_all_books(session: Session = Depends(get_session)):
    return book_service.get_all_books(session)

# 2. Protected Route (Only logged in users can create)
@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book)
def create_book(
    book_data: BookCreateModel, 
    session: Session = Depends(get_session),
    user_details = Depends(access_token_bearer) # 🔒 Lock added here
):
    return book_service.create_book(book_data, session)

# 3. Public Route (Anyone can read a specific book)
@book_router.get("/{book_uid}", response_model=Book)
def get_book(book_uid: str, session: Session = Depends(get_session)):
    book = book_service.get_book(book_uid, session)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# 4. Protected Route (Only logged in users can update)
@book_router.patch("/{book_uid}", response_model=Book)
def update_book(
    book_uid: str, 
    update_data: BookUpdateModel, 
    session: Session = Depends(get_session),
    user_details = Depends(access_token_bearer) # 🔒 Lock added here
):
    updated_book = book_service.update_book(book_uid, update_data, session)
    if not updated_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated_book

# 5. Protected Route (Only logged in users can delete)
@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_uid: str, 
    session: Session = Depends(get_session),
    user_details = Depends(access_token_bearer) # 🔒 Lock added here
):
    deleted = book_service.delete_book(book_uid, session)
    if not deleted:
        raise HTTPException(status_code=404, detail="Book not found")
    return None