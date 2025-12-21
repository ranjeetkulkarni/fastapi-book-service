from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str

    model_config = SettingsConfigDict(
        # 1. Start at this file's location (src/config.py)
        # 2. Go up one level (..) to the root folder
        # 3. Look for the file named ".env"
        env_file=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')),
        extra="ignore"
    )

Config = Settings()