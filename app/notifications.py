import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging
from sqlalchemy.orm import Session

from app import models, schemas, crud
from app.config import settings

logger = logging.getLogger(__name__)

async def send_email_notification(to_email: str, subject: str, body: str) -> bool:
    """
    Send an email notification.
    Returns True if email was sent successfully, False otherwise.
    """
    # In development/testing, just log the email
    if settings.EMAIL_USERNAME == "your_email@gmail.com":
        logger.info(f"Email notification would be sent to {to_email}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Body: {body}")
        return True
    
    # In production, send actual email
    try:
        message = MIMEMultipart()
        message["From"] = settings.EMAIL_FROM
        message["To"] = to_email
        message["Subject"] = subject
        
        # Add body to email
        message.attach(MIMEText(body, "plain"))
        
        # Create secure connection and send email
        context = ssl.create_default_context()
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.starttls(context=context)
            server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, to_email, message.as_string())
            
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False


async def create_system_notification(
    db: Session, 
    user_id: int, 
    message: str, 
    job_id: Optional[int] = None
) -> models.Notification:
    """
    Create a system notification in the database
    """
    notification = schemas.NotificationCreate(
        user_id=user_id,
        job_id=job_id,
        message=message
    )
    return crud.create_notification(db, notification)


async def notify_job_completion(db: Session, job: models.Job) -> bool:
    """
    Notify user about job completion through system notification and email
    """
    # Get user
    user = crud.get_user(db, job.user_id)
    if not user:
        logger.error(f"User {job.user_id} not found for job {job.id}")
        return False
    
    # Determine message based on status
    if job.status == models.JobStatus.COMPLETED.value:
        message = f"Your job (ID: {job.id}) has been completed successfully."
    else:  # FAILED
        message = f"Your job (ID: {job.id}) has failed to process."
    
    # Create system notification
    await create_system_notification(db, user.id, message, job.id)
    
    # Send email notification
    subject = f"AI Service Job {job.status.capitalize()}"
    body = f"""
    Hello {user.username},
    
    {message}
    
    You can check the results in your dashboard.
    
    Thank you for using our AI service!
    """
    
    return await send_email_notification(user.email, subject, body)