from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from .schemas import UserCreate, UserResponse
from .service import UserService
# FIX: Point to db.main, not just db
from db.main import get_session 

router = APIRouter(
    tags=["Authentication"]
)

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, session: Session = Depends(get_session)):
    
    # 1. Init Service with the session
    service = UserService(session)

    # 2. Check if email exists
    if service.user_exists(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with this email already exists"
        )

    # 3. Create User
    new_user = service.create_user(user_data)

    return new_user