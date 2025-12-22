from sqlmodel import Session, select
from fastapi import HTTPException, status
from db.models import Review, Book 
from .schemas import ReviewCreateModel
import uuid

class ReviewService:
    
    # 1. Add a Review
    def add_review(self, user_uid: uuid.UUID, book_uid: uuid.UUID, review_data: ReviewCreateModel, session: Session):
        # A. Check if the book actually exists
        book = session.get(Book, book_uid)
        
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Book not found"
            )
        
        # B. Create the Review Model
        new_review = Review(
            **review_data.model_dump(),
            user_uid=user_uid,
            book_uid=book_uid
        )
        
        session.add(new_review)
        session.commit()
        session.refresh(new_review)
        return new_review

    # 2. Get all reviews (Optional, for testing)
    def get_all_reviews(self, session: Session):
        statement = select(Review).order_by(Review.created_at.desc())
        return session.exec(statement).all()