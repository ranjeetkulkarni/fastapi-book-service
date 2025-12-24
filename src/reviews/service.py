from sqlmodel import Session, select, desc
from db.models import Review, Book
from .schemas import ReviewCreateModel
from errors import ReviewNotFound, BookNotFound
import uuid

class ReviewService:
    def get_all_reviews(self, session: Session):
        statement = select(Review).order_by(desc(Review.created_at))
        return session.exec(statement).all()

    # ✅ ADDED THIS (Fixes the crash)
    def get_review(self, review_uid: str, session: Session):
        try:
            uid_obj = uuid.UUID(review_uid)
        except ValueError:
            return None
            
        statement = select(Review).where(Review.uid == uid_obj)
        return session.exec(statement).first()

    def add_review_to_book(self, user_uid: str, book_uid: str, review_data: ReviewCreateModel, session: Session):
        try:
            book_uid_obj = uuid.UUID(book_uid)
            user_uid_obj = uuid.UUID(user_uid)
        except ValueError:
            raise BookNotFound()

        book_statement = select(Book).where(Book.uid == book_uid_obj)
        book = session.exec(book_statement).first()
        
        if not book:
            raise BookNotFound()
            
        review_data_dict = review_data.model_dump()
        new_review = Review(**review_data_dict)
        new_review.user_uid = user_uid_obj
        new_review.book_uid = book_uid_obj
        
        session.add(new_review)
        session.commit()
        session.refresh(new_review)
        return new_review

    # ✅ ADDED THIS
    def delete_review(self, review_uid: str, session: Session):
        review = self.get_review(review_uid, session)
        
        if not review:
            raise ReviewNotFound()
            
        session.delete(review)
        session.commit()
        return None