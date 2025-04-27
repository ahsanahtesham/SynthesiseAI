from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from sqlalchemy import desc

from app import models, schemas
from app.auth import get_password_hash


# ---- User CRUD ----

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get a user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get a user by email."""
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get a user by username."""
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Get all users with pagination."""
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user."""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_credits(db: Session, user_id: int, amount: int) -> models.User:
    """Update user credits (add or subtract)."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.credits += amount
    if db_user.credits < 0:
        db_user.credits = 0
    
    db.commit()
    db.refresh(db_user)
    return db_user


# ---- Job CRUD ----

def create_job(db: Session, job: schemas.JobCreate, user_id: int, credits_used: int = 1) -> models.Job:
    """Create a new job."""
    db_job = models.Job(
        user_id=user_id,
        document_text=job.document_text,  # Make sure this properly stores the document text
        max_summary_length=job.max_summary_length,  # Add this parameter
        status=models.JobStatus.PENDING.value,
        credits_used=credits_used
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def get_job(db: Session, job_id: int) -> Optional[models.Job]:
    """Get a job by ID."""
    return db.query(models.Job).filter(models.Job.id == job_id).first()


def get_user_jobs(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Job]:
    """Get all jobs for a user with pagination."""
    return db.query(models.Job)\
        .filter(models.Job.user_id == user_id)\
        .order_by(desc(models.Job.created_at))\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_pending_jobs(db: Session, limit: int = 10) -> List[models.Job]:
    """Get pending jobs for processing."""
    return db.query(models.Job)\
        .filter(models.Job.status == models.JobStatus.PENDING.value)\
        .order_by(models.Job.created_at)\
        .limit(limit)\
        .all()


def update_job_status(db: Session, job_id: int, status: models.JobStatus, result: Optional[str] = None) -> models.Job:
    """Update job status and result."""
    db_job = get_job(db, job_id)
    if not db_job:
        return None
    
    db_job.status = status.value
    
    if result is not None:
        db_job.result = result
    
    if status in [models.JobStatus.COMPLETED, models.JobStatus.FAILED]:
        db_job.processed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_job)
    return db_job


# ---- Notification CRUD ----

def create_notification(db: Session, notification: schemas.NotificationCreate) -> models.Notification:
    """Create a new notification."""
    db_notification = models.Notification(
        user_id=notification.user_id,
        job_id=notification.job_id,
        message=notification.message
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def get_user_notifications(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Notification]:
    """Get all notifications for a user with pagination."""
    return db.query(models.Notification)\
        .filter(models.Notification.user_id == user_id)\
        .order_by(desc(models.Notification.created_at))\
        .offset(skip)\
        .limit(limit)\
        .all()


def mark_notification_as_read(db: Session, notification_id: int) -> models.Notification:
    """Mark a notification as read."""
    db_notification = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if not db_notification:
        return None
    
    db_notification.is_read = True
    db.commit()
    db.refresh(db_notification)
    return db_notification


# ---- API Usage CRUD ----

def log_api_usage(db: Session, usage: schemas.APIUsageCreate) -> models.APIUsage:
    """Log API usage."""
    db_usage = models.APIUsage(
        user_id=usage.user_id,
        endpoint=usage.endpoint,
        credits_used=usage.credits_used
    )
    db.add(db_usage)
    db.commit()
    db.refresh(db_usage)
    return db_usage


def get_user_api_usage(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.APIUsage]:
    """Get API usage for a user with pagination."""
    return db.query(models.APIUsage)\
        .filter(models.APIUsage.user_id == user_id)\
        .order_by(desc(models.APIUsage.timestamp))\
        .offset(skip)\
        .limit(limit)\
        .all()