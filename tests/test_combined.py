import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app import auth, models, crud

# Setup test client
client = TestClient(app)

def test_user_authentication_flow():
    """Test user authentication and token generation"""
    # Create a mock password hash
    password = "testpassword"
    hashed_password = auth.get_password_hash(password)
    
    # Test password verification
    assert auth.verify_password(password, hashed_password)
    
    # Create an access token
    token = auth.create_access_token({"sub": "testuser"})
    
    # Verify token generation
    assert token is not None
    assert isinstance(token, str)