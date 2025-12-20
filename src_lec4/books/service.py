from sqlmodel import Session, select, desc
from .models import Book
from .schemas import BookCreateModel, BookUpdateModel
from datetime import datetime

class BookService:
    def get_all_books(self, session: Session):
        statement = select(Book).order_by(desc(Book.created_at))
        result = session.exec(statement)
        return result.all()

    def get_book(self, book_uid: str, session: Session):
        statement = select(Book).where(Book.uid == book_uid)
        result = session.exec(statement)
        return result.first()

    def create_book(self, book_data: BookCreateModel, session: Session):
        # Maps user input to the database table
        new_book = Book(**book_data.model_dump())
        
        session.add(new_book)      # Stage for Neon
        session.commit()           # Physically save
        session.refresh(new_book)  # Get generated UUID/Time back
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