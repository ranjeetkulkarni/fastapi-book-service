from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from typing import List
from db.main import get_session
from .service import BookService
from .schemas import Book, BookCreateModel, BookUpdateModel
# --- UPDATED IMPORTS ---
from auth.dependencies import AccessTokenBearer, RoleChecker

book_router = APIRouter()
book_service = BookService() 
access_token_bearer = AccessTokenBearer()

# --- DEFINE PERMISSIONS ---
# For actions allowed by BOTH Users and Admins
role_checker = RoleChecker(["admin", "user"]) 
# For actions allowed ONLY by Admins
admin_role_checker = RoleChecker(["admin"])   

# 1. Public Route (Anyone can read)
@book_router.get("/", response_model=List[Book])
def get_all_books(session: Session = Depends(get_session)):
    return book_service.get_all_books(session)

# 2. Protected Route (Users & Admins)
@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book,
                  dependencies=[Depends(role_checker)]) # <--- The Lock
def create_book(
    book_data: BookCreateModel, 
    session: Session = Depends(get_session),
    user_details = Depends(access_token_bearer)
):
    return book_service.create_book(book_data, session)

# 3. Public Route
@book_router.get("/{book_uid}", response_model=Book)
def get_book(book_uid: str, session: Session = Depends(get_session)):
    book = book_service.get_book(book_uid, session)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# 4. Protected Route (Users & Admins)
@book_router.patch("/{book_uid}", response_model=Book,
                   dependencies=[Depends(role_checker)]) # <--- The Lock
def update_book(
    book_uid: str, 
    update_data: BookUpdateModel, 
    session: Session = Depends(get_session),
    user_details = Depends(access_token_bearer)
):
    updated_book = book_service.update_book(book_uid, update_data, session)
    if not updated_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated_book

# 5. ADMIN ONLY Route (Strict Lock)
@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT,
                    dependencies=[Depends(admin_role_checker)]) # <--- ADMIN ONLY
def delete_book(
    book_uid: str, 
    session: Session = Depends(get_session),
    user_details = Depends(access_token_bearer)
):
    deleted = book_service.delete_book(book_uid, session)
    if not deleted:
        raise HTTPException(status_code=404, detail="Book not found")
    return None