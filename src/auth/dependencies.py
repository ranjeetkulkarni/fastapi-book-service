from fastapi import Request, status, HTTPException, Depends
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from .utils import decode_token
from db.redis import token_in_blocklist
from sqlmodel import Session
from db.main import get_session
from .service import UserService
from typing import List
from .models import User

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        creds: HTTPAuthorizationCredentials = await super().__call__(request)
        token = creds.credentials
        token_data = decode_token(token)

        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or expired token"
            )
        
        # --- NEW CHECK: IS TOKEN REVOKED? ---
        # We look for 'jti' (JWT ID) in the token data
        jti = token_data.get('jti')
        
        if jti and await token_in_blocklist(jti):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This token has been revoked (Logged out)"
            )
        # ------------------------------------

        self.verify_token_data(token_data)

        return token_data

    def verify_token_data(self, token_data: dict):
        raise NotImplementedError("Please Override this method in child classes")

class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict):
        if token_data and token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an access token"
            )

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict):
        if token_data and not token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a refresh token"
            )
        
# --- NEW FUNCTION ---
async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()), # 1. Get Token Data
    session: Session = Depends(get_session)             # 2. Get DB Connection
):
    user_email = token_details['user']['email']
    
    user_service = UserService(session)
    user = user_service.get_user_by_email(user_email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    return user # Returns the full User model (with password, role, etc.)

# --- NEW CLASS: ROLE CHECKER ---
class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):
        if current_user.role in self.allowed_roles:
            return True
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )