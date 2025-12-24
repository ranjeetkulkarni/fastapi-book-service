from fastapi import APIRouter, Depends, status, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlmodel import Session
from datetime import datetime, timedelta
from celery_tasks import send_email_task
from db.main import get_session 
from .schemas import UserCreate, UserResponse, UserLoginModel
from .service import UserService
from .utils import create_access_token, verify_password
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user
from db.redis import add_jti_to_blocklist
from mail import create_url_safe_token, decode_url_safe_token
from config import Config
# ✅ Make sure UserAlreadyExists is imported
from errors import InvalidCredentials, UserNotFound, InvalidToken, UserAlreadyExists

router = APIRouter() 

error_400 = {400: {"description": "Invalid credentials"}}
error_401 = {401: {"description": "Invalid token"}}
error_404 = {404: {"description": "Not found"}} 
error_409 = {409: {"description": "User already exists"}}

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED, responses=error_409)
async def signup(
    user_data: UserCreate, 
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    service = UserService(session)
    
    # ✅ FIX: Check both Email AND Username
    if service.user_exists(user_data.email, user_data.username):
        raise UserAlreadyExists()

    new_user = service.create_user(user_data)
    
    # ✅ FIX: Safe Email Sending (Won't crash if Redis is down)
    try:
        token = create_url_safe_token({"email": new_user.email})
        link = f"{Config.DOMAIN}/api/v1/auth/verify/{token}"
        send_email_task.delay(email=new_user.email, link=link)
    except Exception as e:
        # Log it, but don't crash the User Creation
        print(f"⚠️ Warning: Email task failed: {e}")
        
    return new_user

@router.post("/login", responses=error_400)
async def login(user_data: UserLoginModel, session: Session = Depends(get_session)):
    service = UserService(session)
    user = service.get_user_by_email(user_data.email)
    
    if not user or not verify_password(user_data.password, user.password_hash):
        raise InvalidCredentials()
    
    access_token = create_access_token(
        user_data={"email": user.email, "user_uid": str(user.uid), "role": user.role},
        expiry=timedelta(minutes=60)
    )
    refresh_token = create_access_token(
        user_data={"email": user.email, "user_uid": str(user.uid)},
        expiry=timedelta(days=2),
        refresh=True
    )
    return JSONResponse(content={
        "message": "Login Successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {"email": user.email, "uid": str(user.uid)}
    })

@router.get("/verify/{token}", responses={**error_401, **error_404}) 
async def verify_user_account(token: str, session: Session = Depends(get_session)):
    token_data = decode_url_safe_token(token)
    if not token_data:
        raise InvalidToken()
    user_email = token_data.get("email")
    service = UserService(session)
    user = service.get_user_by_email(user_email)
    if not user:
        raise UserNotFound()
    if user.is_verified:
        return JSONResponse(content={"message": "Account already verified"}, status_code=status.HTTP_200_OK)
    service.update_user(user, {"is_verified": True})
    return JSONResponse(content={"message": "Account verified successfully"}, status_code=status.HTTP_200_OK)

@router.get("/refresh_token", responses=error_401)
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details['exp']
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(
            user_data=token_details['user'],
            expiry=timedelta(minutes=60)
        )
        return JSONResponse(content={"access_token": new_access_token})
    raise InvalidCredentials() 

@router.post("/logout", status_code=status.HTTP_200_OK, responses=error_401)
async def logout(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details.get('jti')
    await add_jti_to_blocklist(jti)
    return JSONResponse(content={"message": "Logged Out Successfully"}, status_code=status.HTTP_200_OK)

@router.get("/me", response_model=UserResponse, responses=error_401)
async def get_current_user_profile(user = Depends(get_current_user)):
    return user