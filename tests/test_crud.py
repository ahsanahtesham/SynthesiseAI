import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import crud, models, schemas

def test_get_user():
    # Create a mock database session
    mock_db = MagicMock()
    
    # Create a mock user
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.email = "test@example.com"
    mock_user.username = "testuser"
    
    # Set up mock query results
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    # Test get_user function
    result = crud.get_user(mock_db, 1)
    
    # Verify result
    assert result == mock_user
    mock_db.query.assert_called_once_with(models.User)

@patch('app.crud.get_password_hash')
def test_create_user(mock_hash):
    # Setup
    mock_db = MagicMock()
    mock_hash.return_value = "hashed_password"
    
    # Create test data
    user_data = schemas.UserCreate(
        email="new@example.com",
        username="newuser",
        password="password123"
    )
    
    # Call function
    crud.create_user(mock_db, user_data)
    
    # Verify
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    mock_hash.assert_called_once_with("password123")