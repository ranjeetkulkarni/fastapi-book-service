from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session
from datetime import timedelta

from db.main import get_session 
from .schemas import UserCreate, UserResponse, UserLoginModel
from .service import UserService
from .utils import create_access_token, verify_password
# --- NEW IMPORTS ---
from .dependencies import RefreshTokenBearer, AccessTokenBearer
from db.redis import add_jti_to_blocklist

# Standard naming convention inside the module
router = APIRouter() 

# --- SIGNUP ROUTE ---
@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, session: Session = Depends(get_session)):
    service = UserService(session)
    
    # 1. Check if user already exists
    if service.user_exists(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="User with this email already exists"
        )
    
    # 2. Create the user
    new_user = service.create_user(user_data)
    
    return new_user

# --- LOGIN ROUTE ---
@router.post("/login")
async def login(user_data: UserLoginModel, session: Session = Depends(get_session)):
    service = UserService(session)
    
    # 1. Fetch user by email
    user = service.get_user_by_email(user_data.email)
    
    # 2. Verify: User exists AND password matches hash
    if not user or not verify_password(user_data.password, user.password_hash):
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Email or Password"
        )
    
    # 3. Create Access Token (Short-lived: 60 mins)
    access_token = create_access_token(
        user_data={
            "email": user.email,
            "user_uid": str(user.uid)
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

    # 5. Return Tokens
    return JSONResponse(content={
        "message": "Login Successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "email": user.email, 
            "uid": str(user.uid)
        }
    })

# --- REFRESH TOKEN ROUTE (NEW) ---
@router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    """
    Uses a valid Refresh Token to generate a NEW Access Token.
    """
    expiry_timestamp = token_details['exp']

    # 1. Generate a NEW Access Token
    new_access_token = create_access_token(
        user_data=token_details['user'], # Reuse email/uid from the refresh token
        expiry=timedelta(minutes=60)
    )

    return JSONResponse(content={
        "access_token": new_access_token
    })

# --- LOGOUT ROUTE (REVOKE TOKEN) ---
@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    token_details: dict = Depends(AccessTokenBearer())
):
    """
    Adds the current Access Token's JTI to the Redis Blocklist.
    This effectively invalidates the token immediately.
    """
    jti = token_details.get('jti')
    
    # Add to Redis
    await add_jti_to_blocklist(jti)
    
    return JSONResponse(
        content={"message": "Logged Out Successfully"},
        status_code=status.HTTP_200_OK
    )