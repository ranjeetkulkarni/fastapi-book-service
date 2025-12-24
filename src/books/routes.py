from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from typing import List
import uuid
from db.main import get_session
from .service import BookService
from .schemas import Book, BookCreateModel, BookUpdateModel, BookDetailModel
from auth.dependencies import access_token_bearer, RoleChecker, AccessTokenBearer

book_router = APIRouter()
book_service = BookService()
role_checker = RoleChecker(["admin", "user"])
admin_role_checker = RoleChecker(["admin"])

# Define common errors to document
error_404 = {404: {"description": "Book not found"}}
error_401 = {401: {"description": "Not authenticated"}}
error_403 = {403: {"description": "Not authorized"}}

@book_router.get("/", response_model=List[Book])
def get_all_books(session: Session = Depends(get_session)):
    return book_service.get_all_books(session)

@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book, dependencies=[Depends(role_checker)], responses={**error_401, **error_403})
def create_book(
    book_data: BookCreateModel, 
    session: Session = Depends(get_session),
    user_details = Depends(access_token_bearer)
):
    user_uid = user_details['user']['user_uid']
    return book_service.create_book(book_data, user_uid, session)

@book_router.get("/{book_uid}", response_model=BookDetailModel, responses=error_404)
def get_book(book_uid: uuid.UUID, session: Session = Depends(get_session)):
    return book_service.get_book(str(book_uid), session)

@book_router.patch("/{book_uid}", response_model=Book, dependencies=[Depends(role_checker)], responses={**error_404, **error_401, **error_403})
def update_book(
    book_uid: uuid.UUID, 
    update_data: BookUpdateModel, 
    session: Session = Depends(get_session),
    user_details = Depends(access_token_bearer)
):
    return book_service.update_book(str(book_uid), update_data, session)

@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(admin_role_checker)], responses={**error_404, **error_401, **error_403})
def delete_book(
    book_uid: uuid.UUID, 
    session: Session = Depends(get_session),
    user_details = Depends(access_token_bearer)
):
    book_service.delete_book(str(book_uid), session)
    return None

@book_router.get("/user/{user_uid}", response_model=List[Book], responses={**error_401})
def get_books_by_user_uid(
    user_uid: uuid.UUID, 
    session: Session = Depends(get_session),
    user_details = Depends(access_token_bearer)
):
    return book_service.get_user_books(str(user_uid), session)