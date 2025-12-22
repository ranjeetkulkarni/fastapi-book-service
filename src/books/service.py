# 1. ADD 'desc' HERE
from sqlmodel import Session, select, desc 
from datetime import datetime
from db.models import Book
from .schemas import BookCreateModel, BookUpdateModel
import uuid

class BookService:
    def get_all_books(self, session: Session):
        # Now 'desc' works because we imported it!
        statement = select(Book).order_by(desc(Book.created_at))
        result = session.exec(statement).all()
        return result

    # ... [Keep the rest of your functions create_book, get_book, etc.] ...
    def create_book(self, book_data: BookCreateModel, user_uid: str, session: Session):
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)
        new_book.user_uid = uuid.UUID(user_uid)
        
        session.add(new_book)
        session.commit()
        session.refresh(new_book)
        return new_book

    def get_user_books(self, user_uid: str, session: Session):
        statement = select(Book).where(Book.user_uid == uuid.UUID(user_uid))
        result = session.exec(statement).all()
        return result

    def get_book(self, book_uid: str, session: Session):
        statement = select(Book).where(Book.uid == uuid.UUID(book_uid))
        result = session.exec(statement).first()
        return result

    def update_book(self, book_uid: str, update_data: BookUpdateModel, session: Session):
        book = self.get_book(book_uid, session)
        if not book:
            return None
        
        book_data = update_data.model_dump(exclude_unset=True)
        for key, value in book_data.items():
            setattr(book, key, value)
            
        session.add(book)
        session.commit()
        session.refresh(book)
        return book

    def delete_book(self, book_uid: str, session: Session):
        book = self.get_book(book_uid, session)
        if not book:
            return None
            
        session.delete(book)
        session.commit()
        return True