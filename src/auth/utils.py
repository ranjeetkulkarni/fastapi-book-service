from passlib.context import CryptContext
from datetime import timedelta, datetime
import jwt
from config import Config
import uuid
import logging

# 1. Hashing Logic
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_passwd_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 2. Token Logic (The "Ticket Printer")
def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False):
    payload = {}
    
    payload["user"] = user_data
    payload["exp"] = datetime.now() + (
        expiry if expiry is not None else timedelta(seconds=60)
    )
    payload["jti"] = str(uuid.uuid4()) # Unique ID for this token
    payload["refresh"] = refresh

    # Encode the token using our secret key
    token = jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM
    )
    return token

# 3. Decode Logic (The "Bouncer")
def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    
    except jwt.PyJWTError as e:
        logging.exception(e) # Log specific JWT errors
        return None
        
    except Exception as e:
        # ✅ CRITICAL FIX: Catches "ValueError", "DecodeError", and garbage data
        logging.exception(e) 
        return None