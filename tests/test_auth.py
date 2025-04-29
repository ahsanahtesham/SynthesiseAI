import pytest
import sys
import os
from unittest.mock import MagicMock

# Add the parent directory to Python path so it can find the app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import auth

def test_password_verification():
    # Simple password verification test
    password = "testpassword123"
    hashed_password = auth.get_password_hash(password)
    
    # Test correct password verification
    assert auth.verify_password(password, hashed_password) == True
    
    # Test incorrect password verification
    assert auth.verify_password("wrongpassword", hashed_password) == False