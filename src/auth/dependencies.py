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
from errors import (
    InvalidToken, 
    RefreshTokenRequired, 
    UserNotFound, 
    InsufficientPermission
)

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        creds: HTTPAuthorizationCredentials = await super().__call__(request)
        token = creds.credentials
        token_data = decode_token(token)

        if not token_data:
            raise InvalidToken()

        jti = token_data.get('jti')
        if jti and await token_in_blocklist(jti):
            raise InvalidToken()

        self.verify_token_data(token_data)
        return token_data

    def verify_token_data(self, token_data: dict):
        raise NotImplementedError("Override this method")

class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict):
        if token_data and token_data.get("refresh"):
            raise InvalidToken()

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict):
        if token_data and not token_data.get("refresh"):
            raise RefreshTokenRequired()

# --------------------------------------------------------------------------
# 1. CREATE GLOBAL INSTANCES (The "Guards")
# --------------------------------------------------------------------------
access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()

# 2. USE THE INSTANCE HERE
async def get_current_user(
    token_details: dict = Depends(access_token_bearer), # <--- Instance!
    session: Session = Depends(get_session)
):
    user_email = token_details['user']['email']
    user_service = UserService(session)
    user = user_service.get_user_by_email(user_email)
    
    if not user:
        raise UserNotFound()
    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):
        if current_user.role in self.allowed_roles:
            return True
        raise InsufficientPermission()