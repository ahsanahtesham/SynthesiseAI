import asyncio
import threading
import time
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from app import models, crud
from app.database import SessionLocal
from app.external_api import generate_ai_response
from app.notifications import notify_job_completion

logger = logging.getLogger(__name__)

# Simple in-memory queue for job processing
job_queue = asyncio.Queue()
is_processor_running = False

async def add_job_to_queue(job_id: int) -> None:
    """
    Add a job to the processing queue
    """
    await job_queue.put(job_id)
    logger.info(f"Job {job_id} added to queue")


async def process_jobs() -> None:
    """
    Process jobs from the queue
    """
    global is_processor_running
    
    if is_processor_running:
        logger.info("Job processor already running")
        return
    
    is_processor_running = True
    logger.info("Starting job processor")
    
    try:
        while True:
            # Get job from queue
            try:
                job_id = await asyncio.wait_for(job_queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                # Check database for any pending jobs that might have been missed
                db = SessionLocal()
                try:
                    pending_jobs = crud.get_pending_jobs(db, limit=5)
                    for job in pending_jobs:
                        await job_queue.put(job.id)
                        logger.info(f"Added missed job {job.id} to queue")
                finally:
                    db.close()
                    
                # Sleep a bit before checking again
                await asyncio.sleep(5)
                continue
            
            # Process the job
            db = SessionLocal()
            try:
                # Get job from database
                job = crud.get_job(db, job_id)
                if not job:
                    logger.error(f"Job {job_id} not found")
                    job_queue.task_done()
                    continue
                
                # Update job status to processing
                job = crud.update_job_status(db, job.id, models.JobStatus.PROCESSING)
                
                try:
                    logger.info(f"Processing job {job.id} with text: {job.document_text[:50]}...")

                    # Call external AI API
                    response = await generate_ai_response(
                        job.document_text, 
                        max_length=job.max_summary_length or 150
                    )
                    
                    logger.info(f"API response: {response}")
                    
                    if "summary" in response:
                        # Update job with result
                        job = crud.update_job_status(
                            db, 
                            job.id, 
                            models.JobStatus.COMPLETED, 
                            response.get("summary", "No summary generated")
                        )
                        logger.info(f"Job {job.id} completed successfully")
                    else:
                        # Something went wrong
                        error_message = str(response) if response else "No response received"
                        job = crud.update_job_status(
                            db, 
                            job.id, 
                            models.JobStatus.FAILED, 
                            f"Error: Could not generate summary. Response: {error_message}"
                        )
                        logger.error(f"Job {job.id} failed: {error_message}")
    
                    # Notify user
                    await notify_job_completion(db, job)
                    
                except Exception as e:
                    logger.error(f"Error processing job {job.id}: {str(e)}")
                    # Update job as failed
                    job = crud.update_job_status(
                        db, 
                        job.id, 
                        models.JobStatus.FAILED, 
                        f"Error: {str(e)}"
                    )
                    # Notify user about failure
                    await notify_job_completion(db, job)
            
            finally:
                db.close()
                job_queue.task_done()
    
    except Exception as e:
        logger.error(f"Job processor error: {str(e)}")
    finally:
        is_processor_running = False
        logger.info("Job processor stopped")


def start_background_processor() -> None:
    """
    Start background job processor
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(process_jobs())
    finally:
        loop.close()


def initialize_queue_processor() -> None:
    """
    Initialize and start the queue processor in a background thread
    """
    processor_thread = threading.Thread(target=start_background_processor, daemon=True)
    processor_thread.start()
    logger.info("Queue processor initialized in background thread")