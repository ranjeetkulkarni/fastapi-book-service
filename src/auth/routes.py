from fastapi import APIRouter, Depends, status, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlmodel import Session
from datetime import datetime, timedelta # <--- Added datetime import

from db.main import get_session 
from .schemas import UserCreate, UserResponse, UserLoginModel
from .service import UserService
from .utils import create_access_token, verify_password
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user
from db.redis import add_jti_to_blocklist

# --- MAIL IMPORTS ---
from mail import create_url_safe_token, decode_url_safe_token, send_verification_email
from config import Config # Capital 'C' based on your previous config.py
from errors import InvalidCredentials, UserNotFound, UserAlreadyExists, InvalidToken

router = APIRouter() 

# ... imports ...

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate, 
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    service = UserService(session)
    
    new_user = service.create_user(user_data)
    
    token = create_url_safe_token({"email": new_user.email})
    
    link = f"{Config.DOMAIN}/api/v1/auth/verify/{token}"
    
    # --- MOCK EMAIL SENDING ---
    # Instead of sending, we print the link to the console for testing
    print(f"--------------------------------")
    print(f"VERIFICATION LINK FOR {new_user.email}:")
    print(link)
    print(f"--------------------------------")

    # background_tasks.add_task(
    #     send_verification_email, 
    #     emails=[new_user.email], 
    #     link=link
    # )
    
    return new_user

# --- NEW VERIFY ROUTE ---
@router.get("/verify/{token}")
async def verify_user_account(token: str, session: Session = Depends(get_session)):
    # 1. Decode Token
    token_data = decode_url_safe_token(token)
    
    if not token_data:
        raise InvalidToken() 
        
    user_email = token_data.get("email")
    
    # 2. Find User
    service = UserService(session)
    user = service.get_user_by_email(user_email)
    
    if not user:
        raise UserNotFound()
        
    # 3. Check if already verified
    if user.is_verified:
        return JSONResponse(
            content={"message": "Account already verified"}, 
            status_code=status.HTTP_200_OK
        )
        
    # 4. Verify User
    service.update_user(user, {"is_verified": True})
    
    return JSONResponse(
        content={"message": "Account verified successfully"}, 
        status_code=status.HTTP_200_OK
    )

# --- LOGIN ROUTE ---
@router.post("/login")
async def login(user_data: UserLoginModel, session: Session = Depends(get_session)):
    service = UserService(session)
    
    user = service.get_user_by_email(user_data.email)
    
    # Verify using Custom Exception
    if not user or not verify_password(user_data.password, user.password_hash):
        raise InvalidCredentials()
    
    # Create Access Token (Short-lived: 60 mins)
    access_token = create_access_token(
        user_data={
            "email": user.email,
            "user_uid": str(user.uid),
            "role": user.role 
        },
        expiry=timedelta(minutes=60)
    )
    
    # Create Refresh Token (Long-lived: 2 days)
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