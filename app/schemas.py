from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.models import JobStatus

# ---- User Schemas ----

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str


class UserCreate(UserBase):
    """Schema for user creation."""
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str


class UserResponse(UserBase):
    """Schema for user API response."""
    id: int
    credits: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for token payload."""
    username: Optional[str] = None


# ---- Job Schemas ----

class JobBase(BaseModel):
    """Base job schema for document summarization."""
    document_text: str = Field(..., min_length=30, max_length=10000, description="The document text to summarize")
    max_summary_length: Optional[int] = Field(150, ge=30, le=500, description="Maximum length of the summary")


class JobCreate(JobBase):
    """Schema for document summarization job creation."""
    pass

class JobResponse(JobBase):
    """Schema for job API response."""
    id: int
    status: str
    credits_used: int
    created_at: datetime
    processed_at: Optional[datetime] = None
    result: Optional[str] = None
    user_id: int
    
    class Config:
        from_attributes = True


# ---- Notification Schemas ----

class NotificationBase(BaseModel):
    """Base notification schema."""
    message: str


class NotificationCreate(NotificationBase):
    """Schema for notification creation."""
    user_id: int
    job_id: Optional[int] = None


class NotificationResponse(NotificationBase):
    """Schema for notification API response."""
    id: int
    user_id: int
    job_id: Optional[int] = None
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ---- API Usage Schemas ----

class APIUsageCreate(BaseModel):
    """Schema for API usage creation."""
    user_id: int
    endpoint: str
    credits_used: int


class APIUsageResponse(APIUsageCreate):
    """Schema for API usage API response."""
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


# ---- Credit Schemas ----

class CreditUpdate(BaseModel):
    """Schema for credit updates."""
    amount: int = Field(..., description="Amount of credits to add or subtract")


# ---- AI Response Schema ----

class AIResponse(BaseModel):
    """Schema for AI API response."""
    text: str