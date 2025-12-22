from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlmodel import Session
from datetime import timedelta

from db.main import get_session 
from .schemas import UserCreate, UserResponse, UserLoginModel
from .service import UserService
from .utils import create_access_token, verify_password
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user
from db.redis import add_jti_to_blocklist

# 1. IMPORT CUSTOM EXCEPTIONS
from errors import InvalidCredentials, UserNotFound

router = APIRouter() 

# --- SIGNUP ROUTE ---
@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, session: Session = Depends(get_session)):
    service = UserService(session)
    
    # NOTE: We removed the "if user_exists" check here.
    # The Service class now handles that logic and raises UserAlreadyExists automatically!
    new_user = service.create_user(user_data)
    
    return new_user

# --- LOGIN ROUTE ---
@router.post("/login")
async def login(user_data: UserLoginModel, session: Session = Depends(get_session)):
    service = UserService(session)
    
    user = service.get_user_by_email(user_data.email)
    
    # 2. Verify using Custom Exception
    if not user or not verify_password(user_data.password, user.password_hash):
        # OLD: raise HTTPException(status_code=401...)
        # NEW:
        raise InvalidCredentials()
    
    # 3. Create Access Token (Short-lived: 60 mins)
    access_token = create_access_token(
        user_data={
            "email": user.email,
            "user_uid": str(user.uid),
            "role": user.role 
        },
        expiry=timedelta(minutes=60)
    )
    
    # 4. Create Refresh Token (Long-lived: 2 days)
    refresh_token = create_access_token(
        user_data={
            "email": user.email,
            "user_uid": str(user.uid)
        },
        expiry=timedelta(days=2),
        refresh=True
    )

    return JSONResponse(content={
        "message": "Login Successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "email": user.email, 
            "uid": str(user.uid)
        }
    })

# --- REFRESH TOKEN ROUTE ---
@router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details['exp']

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(
            user_data=token_details['user'],
            expiry=timedelta(minutes=60)
        )
        return JSONResponse(content={"access_token": new_access_token})
    
    # Should catch via dependency, but good as backup
    raise InvalidCredentials() 

# --- LOGOUT ROUTE ---
@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details.get('jti')
    await add_jti_to_blocklist(jti)
    return JSONResponse(
        content={"message": "Logged Out Successfully"},
        status_code=status.HTTP_200_OK
    )

# --- ME ROUTE ---
@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(user = Depends(get_current_user)):
    return user