from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from typing import List
import uuid

from db.main import get_session
from auth.dependencies import AccessTokenBearer
from .schemas import ReviewCreateModel, ReviewModel
from .service import ReviewService

review_router = APIRouter()
review_service = ReviewService()
access_token_bearer = AccessTokenBearer()

# 1. Get All Reviews (Public)
@review_router.get("/", response_model=List[ReviewModel])
def get_all_reviews(session: Session = Depends(get_session)):
    return review_service.get_all_reviews(session)

# 2. Add Review to a Book (Protected)
@review_router.post("/book/{book_uid}", response_model=ReviewModel)
def add_review_to_book(
    book_uid: str, 
    review_data: ReviewCreateModel,
    session: Session = Depends(get_session),
    user_details = Depends(access_token_bearer) # Need token to know WHO is reviewing
):
    # Extract User ID from the token
    user_uid = user_details['user']['user_uid']
    
    return review_service.add_review(
        user_uid=uuid.UUID(user_uid),
        book_uid=uuid.UUID(book_uid),
        review_data=review_data,
        session=session
    )