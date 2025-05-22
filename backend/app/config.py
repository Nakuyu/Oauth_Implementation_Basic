from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # OAuth2 Configuration
    CLIENT_ID: str = os.getenv("CLIENT_ID", "")
    CLIENT_SECRET: str = os.getenv("CLIENT_SECRET", "")
    REDIRECT_URI: str = os.getenv("REDIRECT_URI", "http://localhost:8000/auth/callback")
    
    # Token Configuration
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7     # 1 week
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "12345678901234567890123456789012")
    ALGORITHM: str = "HS256"
    
    # Google OAuth2 specific endpoints
    AUTH_URL: str = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL: str = "https://oauth2.googleapis.com/token"
    USER_INFO_URL: str = "https://www.googleapis.com/oauth2/v3/userinfo"
    
    # Google OAuth2 scopes
    SCOPES: list = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email"
    ]

@lru_cache()
def get_settings():
    return Settings() 