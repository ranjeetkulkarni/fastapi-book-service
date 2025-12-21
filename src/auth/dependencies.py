from fastapi import Request, status, HTTPException
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from .utils import decode_token

class AccessTokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        # 1. Extract the token from the header (e.g., "Bearer eyJhbG...")
        creds: HTTPAuthorizationCredentials = await super().__call__(request)
        token = creds.credentials
        
        # 2. Validate the token
        token_data = self.verify_token(token)
        
        return token_data

    def verify_token(self, token: str) -> dict:
        # Decode the token (this checks signature and expiry)
        token_data = decode_token(token)
        
        # If token is invalid (expired or fake), verify_token returns None
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or expired token"
            )
            
        return token_data