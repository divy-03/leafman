# app/config.py
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/leave_db")
    TEST_DATABASE_URL: str = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "a_very_secret_key")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        case_sensitive = True

settings = Settings()