import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import models, crud

def test_update_job_status():
    # Create mock database
    mock_db = MagicMock()
    
    # Create mock job
    mock_job = MagicMock()
    mock_job.id = 1
    mock_job.status = models.JobStatus.PENDING.value
    
    # Set up mock query result
    mock_db.query.return_value.filter.return_value.first.return_value = mock_job
    
    # Test updating job status to COMPLETED
    result = crud.update_job_status(
        mock_db, 
        1, 
        models.JobStatus.COMPLETED, 
        "Summary result"
    )
    
    # Verify result
    assert mock_job.status == models.JobStatus.COMPLETED.value
    assert mock_job.result == "Summary result"
    assert mock_job.processed_at is not None
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()