from sqlmodel import Session, select
from datetime import datetime
from .models import Book
from .schemas import BookCreateModel, BookUpdateModel
import uuid

class BookService:
    def get_all_books(self, session: Session):
        statement = select(Book).order_by(desc(Book.created_at))
        result = session.exec(statement)
        return result.all()

    def get_book(self, book_uid: str, session: Session):
        statement = select(Book).where(Book.uid == book_uid)
        result = session.exec(statement)
        return result.first()

    def create_book(self, book_data: BookCreateModel, user_uid: str, session: Session):
        book_data_dict = book_data.model_dump()
        
        new_book = Book(**book_data_dict)
        
        # Link the book to the user!
        new_book.user_uid = uuid.UUID(user_uid) 
        
        session.add(new_book)
        session.commit()
        session.refresh(new_book)
        return new_book

    def update_book(self, book_uid: str, update_data: BookUpdateModel, session: Session):
        book_to_update = self.get_book(book_uid, session)
        if book_to_update:
            update_dict = update_data.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(book_to_update, key, value)
            book_to_update.update_at = datetime.now()
            session.commit()
            session.refresh(book_to_update)
        return book_to_update

    def delete_book(self, book_uid: str, session: Session):
        book_to_delete = self.get_book(book_uid, session)
        if book_to_delete:
            session.delete(book_to_delete)
            session.commit()
            return True
        return False
    
    def get_user_books(self, user_uid: str, session: Session):
        statement = select(Book).where(Book.user_uid == uuid.UUID(user_uid))
        result = session.exec(statement).all()
        return result