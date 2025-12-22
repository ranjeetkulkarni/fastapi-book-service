from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from typing import List

from db.main import get_session
from .service import BookService
from .schemas import Book, BookCreateModel, BookUpdateModel, BookDetailModel
from auth.dependencies import AccessTokenBearer, RoleChecker
from errors import BookNotFound # <--- Import Custom Error

book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(["admin", "user"])
admin_role_checker = RoleChecker(["admin"])

@book_router.get("/", response_model=List[Book])
def get_all_books(session: Session = Depends(get_session)):
    return book_service.get_all_books(session)

@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book, dependencies=[Depends(role_checker)])
def create_book(
    book_data: BookCreateModel, 
    session: Session = Depends(get_session),
    user_details = Depends(access_token_bearer)
):
    user_uid = user_details['user']['user_uid']
    return book_service.create_book(book_data, user_uid, session)

@book_router.get("/{book_uid}", response_model=BookDetailModel)
def get_book(book_uid: str, session: Session = Depends(get_session)):
    book = book_service.get_book(book_uid, session)
    
    if not book:
        # Raise the specific error
        raise BookNotFound()
        
    return book

@book_router.patch("/{book_uid}", response_model=Book, dependencies=[Depends(role_checker)])
def update_book(
    book_uid: str, 
    update_data: BookUpdateModel, 
    session: Session = Depends(get_session),
    user_details = Depends(access_token_bearer)
):
    # Service raises BookNotFound if needed, so we just return the result
    return book_service.update_book(book_uid, update_data, session)

@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(admin_role_checker)])
def delete_book(
    book_uid: str, 
    session: Session = Depends(get_session),
    user_details = Depends(access_token_bearer)
):
    # Service raises BookNotFound if needed
    book_service.delete_book(book_uid, session)
    return None

@book_router.get("/user/{user_uid}", response_model=List[Book])
def get_books_by_user_uid(
    user_uid: str,
    session: Session = Depends(get_session),
    user_details = Depends(access_token_bearer)
):
    return book_service.get_user_books(user_uid, session)