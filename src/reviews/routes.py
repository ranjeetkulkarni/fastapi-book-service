from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from typing import List
import uuid # <--- Ensure this is imported
from db.main import get_session
from .service import ReviewService
from .schemas import ReviewModel, ReviewCreateModel
from auth.dependencies import AccessTokenBearer
from errors import ReviewNotFound, BookNotFound

review_router = APIRouter()
review_service = ReviewService()
access_token_bearer = AccessTokenBearer()

error_404 = {404: {"description": "Not found"}}
error_401 = {401: {"description": "Not authenticated"}}

@review_router.get("/", response_model=List[ReviewModel])
def get_all_reviews(session: Session = Depends(get_session)):
    return review_service.get_all_reviews(session)

# ✅ THE FIX: Change 'str' to 'uuid.UUID' to catch garbage IDs
@review_router.get("/{review_uid}", response_model=ReviewModel, responses=error_404)
def get_review(review_uid: uuid.UUID, session: Session = Depends(get_session)):
    review = review_service.get_review(str(review_uid), session)
    if not review:
        raise ReviewNotFound()
    return review

@review_router.post("/book/{book_uid}", response_model=ReviewModel, responses={**error_404, **error_401})
def add_review_to_book(
    book_uid: uuid.UUID, # ✅ UUID here too
    review_data: ReviewCreateModel, 
    session: Session = Depends(get_session),
    user_details = Depends(access_token_bearer)
):
    user_uid = user_details['user']['user_uid']
    return review_service.add_review_to_book(
        user_uid=user_uid,
        book_uid=str(book_uid),
        review_data=review_data,
        session=session
    )

@review_router.delete("/{review_uid}", status_code=status.HTTP_204_NO_CONTENT, responses={**error_404, **error_401})
def delete_review(
    review_uid: uuid.UUID, # ✅ UUID here too
    session: Session = Depends(get_session),
    user_details = Depends(access_token_bearer)
):
    review_service.delete_review(str(review_uid), session)
    return None