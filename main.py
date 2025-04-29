import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import models, schemas, crud, auth
from app.database import engine, get_db, Base
from app.queue import add_job_to_queue, initialize_queue_processor
from app.config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="AI Service API",
    description="API for AI processing services with credit system",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize queue processor on startup
@app.on_event("startup")
def startup_event():
    logger.info("Starting up the application")
    initialize_queue_processor()


# ---- Authentication Routes ----

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get access token (login)
    """
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


# ---- User Routes ----

@app.post("/users/", response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    return crud.create_user(db=db, user=user)


@app.get("/users/me/", response_model=schemas.UserResponse)
async def read_users_me(
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get current user information
    """
    return current_user


@app.put("/users/me/credits/", response_model=schemas.UserResponse)
async def update_credits(
    credit_update: schemas.CreditUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update user credits (admin would use this to add credits)
    """
    updated_user = crud.update_user_credits(db, current_user.id, credit_update.amount)
    return updated_user


# ---- Job Routes ----

@app.post("/jobs/", response_model=schemas.JobResponse)
async def create_job(
    job: schemas.JobCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new document summarization job
    """
    # Calculate credit cost based on document length
    document_length = len(job.document_text.split())
    
    # Base cost + additional cost for longer documents
    credits_cost = settings.COST_PER_REQUEST
    if document_length > 500:
        credits_cost += 1  # Additional credit for longer documents
    if document_length > 2000:
        credits_cost += 1  # Additional credit for very long documents
    
    # Check if user has enough credits
    if not auth.check_user_credits(current_user, credits_cost):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Not enough credits. Required: {credits_cost}, Available: {current_user.credits}"
        )
    
    # Deduct credits
    crud.update_user_credits(db, current_user.id, -credits_cost)
    
    # Create job
    db_job = crud.create_job(db, job, current_user.id, credits_cost)
    
    # Add job to processing queue
    await add_job_to_queue(db_job.id)
    
    # Log API usage
    usage = schemas.APIUsageCreate(
        user_id=current_user.id,
        endpoint="/jobs/",
        credits_used=credits_cost
    )
    crud.log_api_usage(db, usage)
    
    return db_job


@app.get("/jobs/", response_model=List[schemas.JobResponse])
async def read_jobs(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all jobs for the current user
    """
    jobs = crud.get_user_jobs(db, user_id=current_user.id, skip=skip, limit=limit)
    return jobs


@app.get("/jobs/{job_id}", response_model=schemas.JobResponse)
async def read_job(
    job_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific job by ID
    """
    job = crud.get_job(db, job_id=job_id)
    if job is None or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# ---- Notification Routes ----

@app.get("/notifications/", response_model=List[schemas.NotificationResponse])
async def read_notifications(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all notifications for the current user
    """
    notifications = crud.get_user_notifications(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return notifications


@app.put("/notifications/{notification_id}/read", response_model=schemas.NotificationResponse)
async def mark_notification_read(
    notification_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mark a notification as read
    """
    notification = crud.mark_notification_as_read(db, notification_id=notification_id)
    if notification is None or notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


# ---- API Usage Routes ----

@app.get("/usage/", response_model=List[schemas.APIUsageResponse])
async def read_api_usage(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get API usage for the current user
    """
    usage = crud.get_user_api_usage(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return usage


# Root route for API info
@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "name": "AI Service API",
        "version": "1.0.0",
        "description": "API for AI processing services with credit system",
        "documentation": "/docs"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "timestamp": datetime.utcnow()}