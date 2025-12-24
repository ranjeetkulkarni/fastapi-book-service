from sqlmodel import Session, select, desc
from datetime import datetime
from db.models import Book
from .schemas import BookCreateModel, BookUpdateModel
# 1. CRITICAL: Ensure this matches the class in src/errors.py
from errors import BookNotFound 
import uuid

class BookService:
    def get_all_books(self, session: Session):
        statement = select(Book).order_by(desc(Book.created_at))
        return session.exec(statement).all()

    def get_user_books(self, user_uid: str, session: Session):
        statement = select(Book).where(Book.user_uid == uuid.UUID(user_uid))
        return session.exec(statement).all()

    def create_book(self, book_data: BookCreateModel, user_uid: str, session: Session):
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)
        new_book.user_uid = uuid.UUID(user_uid)
        
        session.add(new_book)
        session.commit()
        session.refresh(new_book)
        return new_book

    def get_book(self, book_uid: str, session: Session):
        statement = select(Book).where(Book.uid == uuid.UUID(book_uid))
        book = session.exec(statement).first()
        
        if not book:
            raise BookNotFound()
        return book

    def update_book(self, book_uid: str, update_data: BookUpdateModel, session: Session):
        book = self.get_book(book_uid, session)
        
        book_data = update_data.model_dump(exclude_unset=True)
        for key, value in book_data.items():
            setattr(book, key, value)
            
        session.add(book)
        session.commit()
        session.refresh(book)
        return book

    def delete_book(self, book_uid: str, session: Session):
        book = self.get_book(book_uid, session)
        session.delete(book)
        session.commit()
        return True