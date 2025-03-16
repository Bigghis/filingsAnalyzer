import pytest
from fastapi.testclient import TestClient
import os
import sys
from unittest.mock import Mock, patch

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set testing environment
os.environ["TESTING"] = "1"

from src.api.main import app
from src.api.auth.database import init_db

@pytest.fixture(autouse=True)
def setup_test_db():
    """Setup a fresh test database for each test"""
    # Initialize fresh database
    init_db()
    yield

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def test_user():
    """Return test user data"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }

@pytest.fixture
def test_user_token(client, test_user):
    """Create a user and return their authentication token"""
    # Register the user
    client.post("/api/v1/auth/register", json=test_user)
    
    # Login to get token
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    
    data = response.json()
    return data["access_token"]

@pytest.fixture
def authorized_client(client, test_user_token):
    """Return a client with authorization headers set"""
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {test_user_token}"
    }
    return client

@pytest.fixture
def mock_query_engine():
    """Mock QueryEngine for testing"""
    with patch('src.api.routers.queries.QueryEngine') as mock:
        # Configure the mock
        instance = mock.return_value
        instance.query.return_value = {
            "sample": "query result"
        }
        instance.get_all_queries.return_value = ["risk_factors", "business_description"]
        instance.get_query.return_value = "Sample query text"
        yield mock

@pytest.fixture
def registered_user(client, test_user):
    """Create and return a registered user"""
    response = client.post("/api/v1/auth/register", json=test_user)
    assert response.status_code == 200
    return test_user