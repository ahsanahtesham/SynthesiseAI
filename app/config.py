import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "AS_mTtmzmDDTCfuRZQLgGFUnpPXaXybQwqUPE")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # External AI API
    AI_API_KEY: str = os.getenv("AI_API_KEY", "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")
    AI_API_URL: str = os.getenv("AI_API_URL", "https://api-inference.huggingface.co/models/facebook/bart-large-cnn")
    
    # Redis (for queue)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Email (for notifications)
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_USERNAME: str = os.getenv("EMAIL_USERNAME", "your_email@gmail.com")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "your_app_password")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "your_email@gmail.com")
    
    # Credits system
    DEFAULT_CREDITS: int = 10
    COST_PER_REQUEST: int = 1
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()