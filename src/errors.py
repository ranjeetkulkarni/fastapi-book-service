from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, status
from sqlalchemy.exc import SQLAlchemyError

# ==========================================
# 1. Base Exception Class
# ==========================================
class BooklyException(Exception):
    pass

# ==========================================
# 2. Domain-Specific Exceptions
# ==========================================
class UserAlreadyExists(BooklyException):
    pass

class UserNotFound(BooklyException):
    pass

class BookNotFound(BooklyException):
    pass

class ReviewNotFound(BooklyException):
    pass

class InvalidCredentials(BooklyException):
    pass

class AccessDenied(BooklyException):
    pass

# --- NEW: Auth & Token Exceptions ---
class AccountNotVerified(BooklyException):
    """User tries to login but hasn't verified email"""
    pass

class InvalidToken(BooklyException):
    """Token is fake, expired, or malformed"""
    pass

class RefreshTokenRequired(BooklyException):
    """User tried to use an Access Token where a Refresh Token was needed"""
    pass

class InsufficientPermission(BooklyException):
    """User doesn't have the role (e.g. admin)"""
    pass


# ==========================================
# 3. Exception Handlers (The Logic)
# ==========================================
async def user_already_exists_handler(request: Request, exc: UserAlreadyExists):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"error_code": "USER_EXISTS", "message": "User with this email already exists."}
    )

async def user_not_found_handler(request: Request, exc: UserNotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error_code": "USER_NOT_FOUND", "message": "User not found."}
    )

async def book_not_found_handler(request: Request, exc: BookNotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error_code": "BOOK_NOT_FOUND", "message": "Book not found."}
    )

async def review_not_found_handler(request: Request, exc: ReviewNotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error_code": "REVIEW_NOT_FOUND", "message": "Review not found."}
    )

async def invalid_credentials_handler(request: Request, exc: InvalidCredentials):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error_code": "INVALID_CREDENTIALS", "message": "Invalid email or password."}
    )

async def access_denied_handler(request: Request, exc: AccessDenied):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"error_code": "ACCESS_DENIED", "message": "You do not have permission to perform this action."}
    )

# --- NEW HANDLERS ---
async def account_not_verified_handler(request: Request, exc: AccountNotVerified):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"error_code": "ACCOUNT_NOT_VERIFIED", "message": "Account is not verified. Please check your email."}
    )

async def invalid_token_handler(request: Request, exc: InvalidToken):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"error_code": "INVALID_TOKEN", "message": "Token is invalid or expired."}
    )

async def refresh_token_required_handler(request: Request, exc: RefreshTokenRequired):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"error_code": "REFRESH_TOKEN_REQUIRED", "message": "A valid refresh token is required for this action."}
    )

async def insufficient_permission_handler(request: Request, exc: InsufficientPermission):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"error_code": "INSUFFICIENT_PERMISSIONS", "message": "You do not have the required role."}
    )

# --- GLOBAL HANDLER (The "Catch-All") ---
# This catches random server crashes (Status 500)
async def internal_server_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error_code": "SERVER_ERROR", "message": "Something went wrong on our end."}
    )

# ==========================================
# 4. Registration Function (The Glue)
# ==========================================
def register_all_errors(app: FastAPI):
    app.add_exception_handler(UserAlreadyExists, user_already_exists_handler)
    app.add_exception_handler(UserNotFound, user_not_found_handler)
    app.add_exception_handler(BookNotFound, book_not_found_handler)
    app.add_exception_handler(ReviewNotFound, review_not_found_handler)
    app.add_exception_handler(InvalidCredentials, invalid_credentials_handler)
    app.add_exception_handler(AccessDenied, access_denied_handler)
    
    # Register the New Ones
    app.add_exception_handler(AccountNotVerified, account_not_verified_handler)
    app.add_exception_handler(InvalidToken, invalid_token_handler)
    app.add_exception_handler(RefreshTokenRequired, refresh_token_required_handler)
    app.add_exception_handler(InsufficientPermission, insufficient_permission_handler)
    
    # Register Global Fallback
    app.add_exception_handler(Exception, internal_server_error_handler)
    app.add_exception_handler(SQLAlchemyError, internal_server_error_handler) # Catch DB errors