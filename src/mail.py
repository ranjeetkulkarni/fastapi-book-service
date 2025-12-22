from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
from typing import List
from itsdangerous import URLSafeTimedSerializer
from config import Config
from pathlib import Path

# 1. Email Configuration
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS
)

# 2. Token Logic (ItsDangerous)
serializer = URLSafeTimedSerializer(
    secret_key=Config.SECRET_KEY, 
    salt="email-configuration"
)

def create_url_safe_token(data: dict):
    """
    Creates a time-sensitive string token from a dictionary (e.g., {'email': '...'})
    """
    token = serializer.dumps(data)
    return token

def decode_url_safe_token(token: str):
    """
    Decodes the token. Returns dictionary if valid, raises error if expired/tampered.
    """
    try:
        # Token valid for 1 hour (3600 seconds)
        token_data = serializer.loads(token, max_age=3600)
        return token_data
    except Exception as e:
        print(f"Token Error: {str(e)}")
        return None

# 3. Email Sending Logic
class EmailSchema(BaseModel):
    emails: List[EmailStr]

mail = FastMail(conf)

async def send_verification_email(emails: List[str], link: str):
    """
    Constructs and sends the verification email.
    """
    html = f"""
    <h1>Verify your Bookly Account</h1>
    <p>Please click this <a href="{link}">link</a> to verify your email address.</p>
    <p>This link expires in 1 hour.</p>
    """

    message = MessageSchema(
        subject="Account Verification - Bookly",
        recipients=emails,
        body=html,
        subtype=MessageType.html
    )

    await mail.send_message(message)