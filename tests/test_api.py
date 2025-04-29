import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app import auth, models

# Setup test client
client = TestClient(app)

def test_root_endpoint():
    # Test the root endpoint
    response = client.get("/")
    assert response.status_code == 200
    assert "name" in response.json()
    assert "version" in response.json()

def test_health_check():
    # Test the health check endpoint
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# This is a more appropriate way to test authenticated endpoints in FastAPI
def test_read_users_me_with_token():
    # Create a mock user
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.username = "testuser"
    mock_user.email = "test@example.com"
    mock_user.credits = 10
    
    # Create a valid token
    token = auth.create_access_token(data={"sub": "testuser"})
    
    # We need to override the dependency in the app
    # This is the tricky part with FastAPI
    def override_get_current_active_user():
        return mock_user
    
    # Save the original dependency
    original_dependency = app.dependency_overrides.copy()
    
    try:
        # Override the dependency
        app.dependency_overrides[auth.get_current_active_user] = override_get_current_active_user
        
        # Test the endpoint with the token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/me/", headers=headers)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
    
    finally:
        # Restore original dependencies
        app.dependency_overrides = original_dependency