from fastapi.testclient import TestClient
import pytest

def test_register_user(client, test_user):
    response = client.post("/api/v1/auth/register", json=test_user)
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    assert "password" not in data

def test_register_existing_user(client, test_user, registered_user):
    # Try to register the same user again
    response = client.post("/api/v1/auth/register", json=test_user)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_login_success(client, registered_user):
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": registered_user["username"],
            "password": registered_user["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, registered_user):
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": registered_user["username"],
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_login_nonexistent_user(client):
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "nonexistentuser",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]