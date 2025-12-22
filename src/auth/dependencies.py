from fastapi import Request, Depends
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from .utils import decode_token
from db.redis import token_in_blocklist
from sqlmodel import Session
from db.main import get_session
from .service import UserService
from typing import List
from db.models import User

# 1. IMPORT CUSTOM EXCEPTIONS

from errors import (
    InvalidToken, 
    RefreshTokenRequired, 
    UserNotFound, 
    InsufficientPermission,
    AccountNotVerified
)

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        creds: HTTPAuthorizationCredentials = await super().__call__(request)
        token = creds.credentials
        token_data = decode_token(token)

        if not token_data:
            # OLD: raise HTTPException(403, "Invalid or expired token")
            # NEW:
            raise InvalidToken()

        # --- CHECK REDIS BLOCKLIST ---
        jti = token_data.get('jti')
        
        if jti and await token_in_blocklist(jti):
            # OLD: raise HTTPException(403, "This token has been revoked")
            # NEW:
            raise InvalidToken()
        # ------------------------------------

        self.verify_token_data(token_data)

        return token_data

    def verify_token_data(self, token_data: dict):
        raise NotImplementedError("Please Override this method in child classes")

class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict):
        # If "refresh": true, it's NOT an access token
        if token_data and token_data.get("refresh"):
            # OLD: raise HTTPException(403, "Please provide an access token")
            # NEW: Treat it as an invalid token for this endpoint
            raise InvalidToken()

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict):
        # If "refresh" is missing/false, it's NOT a refresh token
        if token_data and not token_data.get("refresh"):
            # OLD: raise HTTPException(403, "Please provide a refresh token")
            # NEW:
            raise RefreshTokenRequired()

async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()), 
    session: Session = Depends(get_session)
):
    user_email = token_details['user']['email']
    
    user_service = UserService(session)
    user = user_service.get_user_by_email(user_email)
    
    if not user:
        # OLD: raise HTTPException(404, "User not found")
        # NEW:
        raise UserNotFound()
        
    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):
        # Optional: You can enforce verification here too
        # if not current_user.is_verified:
        #     raise AccountNotVerified()

        if current_user.role in self.allowed_roles:
            return True
        
        # OLD: raise HTTPException(403, "You do not have permission...")
        # NEW:
        raise InsufficientPermission()