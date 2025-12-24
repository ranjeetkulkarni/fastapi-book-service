from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    # --- Existing Variables ---
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str

    # --- NEW: Email Settings ---
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    
    # --- NEW: Domain (for verification link) ---
    DOMAIN: str

    REDIS_URL: str = "redis://localhost:6379/0"

    
    model_config = SettingsConfigDict(
        # Your existing environment file logic
        env_file=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')),
        extra="ignore"
    )

# Instantiate
Config = Settings()