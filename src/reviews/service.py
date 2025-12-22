from sqlmodel import Session, select
from db.models import Review, Book 
from .schemas import ReviewCreateModel
from errors import BookNotFound, ReviewNotFound # <--- Import Both
import uuid

class ReviewService:
    
    def add_review(self, user_uid: uuid.UUID, book_uid: uuid.UUID, review_data: ReviewCreateModel, session: Session):
        # Check if book exists
        book = session.get(Book, book_uid)
        
        if not book:
            raise BookNotFound()
        
        new_review = Review(
            **review_data.model_dump(),
            user_uid=user_uid,
            book_uid=book_uid
        )
        
        session.add(new_review)
        session.commit()
        session.refresh(new_review)
        return new_review

    def get_all_reviews(self, session: Session):
        statement = select(Review).order_by(Review.created_at.desc())
        return session.exec(statement).all()