from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Kisan Saarthi"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    CORS_ORIGINS: List[str] = ["*"]
    
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    GROQ_API_KEY: Optional[str] = None
    
    MONGODB_URI: Optional[str] = None
    MONGODB_DB: str = "kisan_saarthi"
    
    REDIS_URL: Optional[str] = None
    
    RATE_LIMIT_PER_MINUTE: int = 30
    
    AGMARKNET_API_KEY: Optional[str] = None
    OPENWEATHER_API_KEY: Optional[str] = None
    
    # Bot Tokens
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_WHATSAPP_NUMBER: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()